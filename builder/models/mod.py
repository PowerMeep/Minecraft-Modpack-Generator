import json
from datetime import datetime, timezone
import logging
import os
import sqlite3

from pytimeparse2 import parse


logger = logging.getLogger()

time_format = '%Y-%m-%dT%H:%M:%S.%f%z'
stale_time = os.environ.get('CACHE_STALE_TIME')
if stale_time is not None:
    try:
        stale_time = parse(stale_time, as_timedelta=True)
    except:
        logger.error(f'Unable to parse cache stale time: {stale_time}')
        stale_time = None

json_path = 'data/mods.json'

db_name = 'data/mod_cache.db'
table_timestamps = 'timestamps'
table_sources = 'sources'
key_name = 'name'
key_date = 'date'
key_version = 'version'
key_metadata = 'metadata'

_validation_data = {
    'name': (str, True),
    'curseforge_id': (int, False)
}


class CFMetadata:
    def __init__(self,
                 display_name: str = None,
                 website_url: str = None,
                 author: str = None):
        self.display_name = display_name
        self.website_url = website_url
        self.author = author

    def from_json(self, obj):
        self.display_name = obj.get('display_name')
        self.website_url = obj.get('website_url')
        self.author = obj.get('author')

    def to_json(self):
        return json.dumps({
            'display_name': self.display_name,
            'website_url': self.website_url,
            'author': self.author
        })


class CFSource:
    def __init__(self,
                 file_id: str = None,
                 file_name: str = None,
                 download_url: str = None,
                 dependencies: list = None):
        self.file_id = file_id
        self.file_name = file_name
        self.download_url = download_url
        self.dependencies = dependencies or []

    def from_json(self, obj):
        self.file_id = obj.get('file_id')
        self.file_name = obj.get('file_name')
        self.download_url = obj.get('download_url')
        self.dependencies = obj.get('dependencies')

    def to_json(self):
        return json.dumps({
            'file_id': self.file_id,
            'file_name': self.file_name,
            'download_url': self.download_url,
            'dependencies': self.dependencies
        })


class Mod:
    def __init__(self,
                 name,
                 curseforge_id: int = None):
        # The id of this mod, relative to this application
        self.name = name

        # The id of this mod on curseforge
        self.curseforge_id = curseforge_id

        # The metadata retrieved from CF
        self.curseforge_meta = None

        # Information for the most recent artifacts
        self.sources_by_version = {}

        # The last time this mod's data was updated
        self.last_update = None

    def clear_sources(self):
        self.sources_by_version.clear()

    def add_source(self,
                   key: str,
                   source: CFSource):
        existing = self.sources_by_version.get(key)
        if not existing:
            self.sources_by_version[key] = source
            logger.info(f'Added source: {key}: {source.download_url}')
        else:
            existing_order = existing.file_name
            source_order = source.file_name
            if existing_order < source_order:
                self.sources_by_version[key] = source
                logger.info(f'Updated source: {key}: {source.download_url}')
            else:
                logger.debug(f'Existing source is more recent: {key}: {source_order} < {existing_order}')

    def is_stale(self):
        if self.last_update is None:
            return True
        if stale_time is None:
            return False
        oldest = datetime.now(timezone.utc) - stale_time
        return self.last_update <= oldest

    def save_sources(self):
        _setup_cache()
        self.last_update = datetime.now(timezone.utc)
        time_str = datetime.strftime(self.last_update, time_format)
        connection = sqlite3.connect(db_name)
        out = None
        if self.curseforge_meta:
            out = self.curseforge_meta.to_json()
        connection.execute(
            f"INSERT INTO {table_timestamps}({key_name}, {key_date}, {key_metadata}) VALUES(?, ?, ?)\n"
            f"ON CONFLICT({key_name}) DO UPDATE SET {key_date}=?, {key_metadata}=?;",
            [self.name, time_str, out, time_str, out]
        )
        connection.commit()

        for version, metadata in self.sources_by_version.items():
            out = metadata.to_json()
            connection.execute(
                f"INSERT INTO {table_sources}({key_name}, {key_version}, {key_metadata})"
                f"  VALUES(?, ?, ?)\n"
                f"ON CONFLICT({key_name}, {key_version}) DO UPDATE SET {key_metadata}=?;",
                [self.name, version, out, out]
            )
        connection.commit()
        connection.close()

    def __str__(self):
        return self.name


mods_by_name = {
    'Vanilla': Mod('Vanilla')
}


def from_json(obj: dict):
    from models.load_util import validate_type
    errors = validate_type(
        obj.get('name'),
        _validation_data,
        obj
    )
    if errors:
        for error in errors:
            logger.error(error)
        return

    m = Mod(
        name=obj.get('name'),
        curseforge_id=obj.get('curseforge_id')
    )
    logger.info(f'Loaded mod: {m.name}')
    mods_by_name[m.name] = m


def load_mods():
    from models.load_util import load_named_items
    load_named_items(json_path, from_json)
    load_cached_sources()


def _setup_cache():
    connection = sqlite3.connect(db_name)
    connection.execute(
        f'CREATE TABLE IF NOT EXISTS {table_timestamps}(\n'
        f'  {key_name}     TEXT PRIMARY KEY,\n'
        f'  {key_date}     TEXT NOT NULL,\n'
        f'  {key_metadata} TEXT NOT NULL\n'
        ');'
    )
    connection.execute(
        f'CREATE TABLE IF NOT EXISTS {table_sources}(\n'
        f'  {key_name}     TEXT NOT NULL,\n'
        f'  {key_version}  TEXT NOT NULL,\n'
        f'  {key_metadata} TEXT NOT NULL,\n'
        f'  PRIMARY KEY ({key_name}, {key_version}),\n'
        f'  CONSTRAINT fk_name\n'
        f'    FOREIGN KEY ({key_name})\n'
        f'    REFERENCES {table_timestamps} ({key_name})\n'
        f'    ON DELETE CASCADE'
        ');'
    )
    connection.commit()
    connection.close()


def load_cached_sources():
    _setup_cache()
    logger.warning('Loading cached mod sources')
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    mods_not_found = set()

    fetch_time_rows = cursor.execute(f'SELECT * FROM {table_timestamps};')
    for row in fetch_time_rows:
        name = row[0]
        date = row[1]
        meta = json.loads(row[2])
        mod: Mod = mods_by_name.get(name)
        if mod is None:
            mods_not_found.add(name)
        else:
            mod.last_update = datetime.strptime(date, time_format)
            mod.curseforge_meta = CFMetadata()
            mod.curseforge_meta.from_json(meta)

    sources_rows = cursor.execute(f'SELECT * FROM {table_sources};')
    for row in sources_rows:
        name    = row[0]
        version = row[1]
        meta    = json.loads(row[2])
        if name in mods_not_found:
            continue

        mod: Mod = mods_by_name.get(name)
        source = CFSource()
        source.from_json(meta)
        mod.add_source(
            key=version,
            source=source
        )

    if len(mods_not_found) > 0:
        logger.warning(f'Removing {len(mods_not_found)} cached mod info')
        q_str = ', '.join(['?']*len(mods_not_found))
        connection.execute(
            f"DELETE FROM {table_timestamps}\n"
            f" WHERE {key_name} IN ({q_str});",
            list(mods_not_found)
        )
    connection.commit()
    connection.close()
