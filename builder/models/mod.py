import logging
import sqlite3
from datetime import datetime, timezone

logger = logging.getLogger()

time_format = '%Y-%m-%dT%H:%M:%S.%f%z'

db_name = 'mod_cache.db'
table_timestamps = 'timestamps'
table_sources = 'sources'
key_name = 'name'
key_date = 'date'
key_version = 'version'
key_url = 'url'


def dict_to_x_list(d) -> list:
    out = []
    for v in d.values():
        out .append('x' if v else ' ')
    return out


class Mod:
    def __init__(self,
                 name,
                 configs=None,
                 curseforge_id: int = None,
                 modrinth_slug: str = None):
        self.name = name
        self.curseforge_id = curseforge_id
        self.modrinth_slug = modrinth_slug
        self.sources = {}
        self.last_update = None

        # file id
        # required (enabled?)
        self.configs = configs or []

    def add_source(self,
                   loader: str,
                   mc_version: str,
                   url: str):
        key = f'{loader}-{mc_version}'
        existing = self.sources.get(key)
        if not existing or existing < url:
            self.sources[key] = url
            logger.info(f'Added source: {key}: {url}')
        else:
            logger.debug(f'Existing source is more recent: {key}: {url} < {existing}')

    def is_stale(self):
        return self.last_update is None

    def save_sources(self):
        _setup_cache()
        self.last_update = datetime.now(timezone.utc)
        time_str = datetime.strftime(self.last_update, time_format)
        connection = sqlite3.connect(db_name)
        connection.execute(
            f"INSERT INTO {table_timestamps}({key_name}, {key_date}) VALUES(?, ?)\n"
            f"ON CONFLICT({key_name}) DO UPDATE SET {key_date}=?;",
            [self.name, time_str, time_str]
        )
        connection.commit()

        for version, url in self.sources.items():
            connection.execute(
                f"INSERT INTO {table_sources}({key_name}, {key_version}, {key_url})"
                f"  VALUES(?, ?, ?)\n"
                f"ON CONFLICT({key_name}, {key_version}) DO UPDATE SET {key_url}=?;",
                [self.name, version, url, url]
            )
        connection.commit()
        connection.close()

    def get_alt_configuration(self, configs):
        mod = Mod(
            name=self.name,
            configs=configs
        )
        return mod

    def __str__(self):
        return self.name


mods_by_name = {
    'Vanilla': Mod('Vanilla')
}


def from_json(obj: dict):
    m = Mod(
        name=obj.get('name'),
        curseforge_id=obj.get('curseforge_id'),
        modrinth_slug=obj.get('modrinth_slug')
    )
    logger.info(f'Loaded mod: {m.name}')
    mods_by_name[m.name] = m


def load_mods():
    from models.load_util import load_named_items
    load_named_items('configs/mods.json', from_json)
    load_cached_sources()


def _setup_cache():
    connection = sqlite3.connect(db_name)
    connection.execute(
        f'CREATE TABLE IF NOT EXISTS {table_timestamps}(\n'
        f'  {key_name} TEXT PRIMARY KEY,\n'
        f'  {key_date} TEXT NOT NULL\n'
        ');'
    )
    connection.execute(
        f'CREATE TABLE IF NOT EXISTS {table_sources}(\n'
        f'  {key_name}    TEXT NOT NULL,\n'
        f'  {key_version} TEXT NOT NULL,\n'
        f'  {key_url}     TEXT NOT NULL,\n'
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
        mod: Mod = mods_by_name.get(name)
        if mod is None:
            mods_not_found.add(name)
        else:
            mod.last_update = datetime.strptime(date, time_format)

    sources_rows = cursor.execute(f'SELECT * FROM {table_sources};')
    for row in sources_rows:
        name    = row[0]
        version = row[1]
        url     = row[2]
        if name in mods_not_found:
            continue

        mod: Mod = mods_by_name.get(name)
        tokens = version.split('-')
        mod.add_source(
            loader=tokens[0],
            mc_version=tokens[1],
            url=url
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