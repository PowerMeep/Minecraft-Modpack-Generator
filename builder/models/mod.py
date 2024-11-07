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
key_date = 'date'
key_version = 'version'
key_metadata = 'metadata'

table_projects = 'cf_projects'
key_project_id = 'project_id'


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
                 file_date: str = None,
                 download_url: str = None,
                 dependencies: list = None):
        self.file_id = file_id
        self.file_name = file_name
        self.file_date = file_date
        self.download_url = download_url
        self.dependencies = dependencies or []

    def from_json(self, obj):
        self.file_id = obj.get('file_id')
        self.file_date = obj.get('file_date')
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
            logger.debug(f'Added source: {key}: {source.download_url}')
        else:
            existing_order = existing.file_date
            source_order = source.file_date
            if existing_order < source_order:
                self.sources_by_version[key] = source
                logger.debug(f'Updated source: {key}: {source.download_url}')
            else:
                logger.debug(f'Existing source is more recent: {key}: {source_order} < {existing_order}')

    def get_best_source(self, version):
        if version in self.sources_by_version:
            return self.sources_by_version.get(version)
        best_third = None
        target_tokens = version.split('.')
        for key, source in self.sources_by_version.items():
            tokens = key.split('.')

            if len(target_tokens) == 1 or len(tokens) == 1:
                continue
            if tokens[1] != target_tokens[1]:
                continue

            if len(tokens) == 3:
                third = int(tokens[2])
            else:
                third = 0

            if best_third is None or best_third < third:
                best_third = third

        if best_third is not None:
            partial_version = '.'.join(target_tokens[:2])
            if best_third == 0:
                return self.sources_by_version.get(partial_version)
            else:
                return self.sources_by_version.get(f'{partial_version}.{best_third}')
        return None

    def is_stale(self):
        if self.last_update is None:
            return True
        if stale_time is None:
            return False
        oldest = datetime.now(timezone.utc) - stale_time
        return self.last_update <= oldest

    def fetch_sources(self,
                      force=False):
        from apis import curseforge
        if force or self.is_stale():
            logger.warning(f'Updating sources for {self.curseforge_id}...')
            files = curseforge.get_files(self.curseforge_id)
            if not files:
                logger.error(f'Could not fetch sources for {self.curseforge_id}')
                return

            self.clear_sources()
            for file in files:
                game_version = None
                for version in file.get('gameVersions'):
                    if version[0].isdigit():
                        game_version = version
                if game_version is None:
                    logger.error('Could not determine version for source')
                    continue

                self.add_source(
                    key=game_version,
                    source=CFSource(
                        file_id=file.get('id'),
                        file_name=file.get('fileName'),
                        file_date=file.get('fileDate'),
                        download_url=file.get('downloadUrl'),
                        dependencies=file.get('dependencies')
                    )
                )

    def save_sources(self):
        _setup_cache()
        self.last_update = datetime.now(timezone.utc)
        time_str = datetime.strftime(self.last_update, time_format)
        connection = sqlite3.connect(db_name)
        out = None
        if self.curseforge_meta:
            out = self.curseforge_meta.to_json()
        connection.execute(
            f"INSERT INTO {table_timestamps}({key_project_id}, {key_date}, {key_metadata}) VALUES(?, ?, ?)\n"
            f"ON CONFLICT({key_project_id}) DO UPDATE SET {key_date}=?, {key_metadata}=?;",
            [self.curseforge_id, time_str, out, time_str, out]
        )
        connection.commit()

        for version, metadata in self.sources_by_version.items():
            out = metadata.to_json()
            connection.execute(
                f"INSERT INTO {table_projects}({key_project_id}, {key_version}, {key_metadata})"
                f"  VALUES(?, ?, ?)\n"
                f"ON CONFLICT({key_project_id}, {key_version}) DO UPDATE SET {key_metadata}=?;",
                [self.curseforge_id, version, out, out]
            )
        connection.commit()
        connection.close()

    def __str__(self):
        return self.name


mods_by_name = {
    'Vanilla': Mod('Vanilla')
}

mods_by_id = {}


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
    if m.curseforge_id:
        mods_by_id[m.curseforge_id] = m


def load_mods():
    from models.load_util import load_named_items
    load_named_items(json_path, from_json)
    load_cached_sources()


def _setup_cache():
    connection = sqlite3.connect(db_name)
    connection.execute(
        f'CREATE TABLE IF NOT EXISTS {table_timestamps}(\n'
        f'  {key_project_id} TEXT PRIMARY KEY,\n'
        f'  {key_date}       TEXT NOT NULL,\n'
        f'  {key_metadata}   TEXT\n'
        ');'
    )
    connection.execute(
        f'CREATE TABLE IF NOT EXISTS {table_projects}(\n'
        f'  {key_project_id}     TEXT NOT NULL,\n'
        f'  {key_version}  TEXT NOT NULL,\n'
        f'  {key_metadata} TEXT NOT NULL,\n'
        f'  PRIMARY KEY ({key_project_id}, {key_version}),\n'
        f'  CONSTRAINT fk_name\n'
        f'    FOREIGN KEY ({key_project_id})\n'
        f'    REFERENCES {table_timestamps} ({key_project_id})\n'
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

    fetch_time_rows = cursor.execute(f'SELECT * FROM {table_timestamps};')
    for row in fetch_time_rows:
        cid = row[0]
        date = row[1]
        meta = row[2]
        meta = json.loads(meta) if meta else None
        mod: Mod = mods_by_id.get(cid)
        if mod is None:
            mod = Mod(
                name=None,
                curseforge_id=cid
            )
            mods_by_id[cid] = mod
        mod.last_update = datetime.strptime(date, time_format)
        mod.curseforge_meta = CFMetadata()
        if meta:
            mod.curseforge_meta.from_json(meta)

    sources_rows = cursor.execute(f'SELECT * FROM {table_projects};')
    for row in sources_rows:
        cid    = row[0]
        version = row[1]
        meta    = json.loads(row[2])

        mod: Mod = mods_by_id.get(cid)
        source = CFSource()
        source.from_json(meta)
        mod.add_source(
            key=version,
            source=source
        )

    connection.commit()
    connection.close()


def fetch_info(mod_ids):
    from apis import curseforge
    existing = [m for m in mod_ids if m in mods_by_id]
    infos_response = curseforge.get_project_info(existing)
    if infos_response.status_code != 200:
        logger.error(f'Could not fetch info: {infos_response.status_code}')
        return
    else:
        info_datas = infos_response.json().get('data')
        for info_data in info_datas:
            mod = mods_by_id.get(info_data.get('id'))
            mod.curseforge_meta = CFMetadata(
                display_name=info_data.get('name'),
                website_url=info_data.get('links').get('websiteUrl')
            )
