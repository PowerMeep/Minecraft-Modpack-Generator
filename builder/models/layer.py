import logging
logger = logging.getLogger()

_validation_data = {
    'name': (str, True),
    'description': (str, False),
    'mods': (list, False),
    'terrain_mod': (list, False),
    'village_mod': (list, False)
}

json_path = 'data/layers.json'


class Layer:
    def __init__(self,
                 name='Unnamed Layer',
                 description='A layer of mods',
                 terrain_mod=None,
                 village_mod=None,
                 mods=None):
        self.name = name
        self.description = description
        self.terrain_mod = terrain_mod
        self.village_mod = village_mod
        self.mods = mods or []

    def __str__(self):
        return self.name

    def add_mod(self, mod):
        from random import choice
        if type(mod) is list:
            mod = choice(mod)[0]
        from models.mod import mods_by_name
        if mod not in self.mods and mod != mods_by_name.get('Vanilla'):
            logger.debug(f'  > Adding mod: {mod.name}')
            self.mods.append(mod)

    def update(self, other_layer):
        if other_layer is None:
            return
        if other_layer == layers_by_name.get('Vanilla'):
            return
        logger.info(f'> Adding layer: {other_layer.name}')
        if other_layer.terrain_mod and not self.terrain_mod:
            self.terrain_mod = other_layer.terrain_mod
        if other_layer.village_mod and not self.village_mod:
            self.village_mod = other_layer.village_mod
        for mod in other_layer.mods:
            self.add_mod(mod)

    def _cache_fetch_curseforge(self):
        from models.mod import Mod, CFMetadata, CFSource
        from apis import curseforge

        mod: Mod
        mods_by_id = {}
        for mod in self.mods:
            if mod.curseforge_id is None:
                logger.error(f'{mod.name} has no Curseforge Id')
                continue

            if not mod.is_stale():
                logger.debug(f'{mod.name} sources are recent enough')
                continue
            else:
                mods_by_id[mod.curseforge_id] = mod

        if len(mods_by_id) == 0:
            return

        logger.warning(f'{len(mods_by_id)} mods are stale and will be updated')
        infos_response = curseforge.get_project_info(list(mods_by_id.keys()))
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

        for mod in mods_by_id.values():
            logger.warning(f'Updating sources for {mod.name}...')
            files_response = curseforge.get_files(mod.curseforge_id)
            if files_response.status_code != 200:
                logger.error(f'Could not fetch files for {mod.name}: {files_response.status_code}')
                continue

            mod.clear_sources()
            for file in files_response.json().get('data'):
                loaders = []
                game_version = None
                for version in file.get('gameVersions'):
                    if version[0].isdigit():
                        game_version = version
                    else:
                        loaders.append(version)
                if game_version is None:
                    logger.error('Could not determine version for file')
                    continue

                if len(loaders) == 0:
                    loaders = ['Forge']

                for loader in loaders:
                    mod.add_source(
                        key=f'{loader}-{game_version}',
                        source=CFSource(
                            file_id=file.get('id'),
                            file_name=file.get('fileName'),
                            download_url=file.get('downloadUrl'),
                            dependencies=file.get('dependencies')
                        )
                    )
            mod.save_sources()

    def fetch_metadata(self):
        self._cache_fetch_curseforge()


layers_by_name = {
    'Vanilla': Layer('Vanilla')
}


def _get_mods(element):
    from models.load_util import get_item
    from models.mod import mods_by_name
    return get_item(
        element=element,
        element_type='mod',
        store=mods_by_name
    )


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

    logger.info(f'Loading Layer: {obj.get("name")}')
    l = Layer(
        name=obj.get('name'),
        description=obj.get('description'),
        terrain_mod=_get_mods(obj.get('terrain_mod')),
        village_mod=_get_mods(obj.get('village_mod')),
        mods=_get_mods(obj.get('mods'))
    )
    layers_by_name[l.name] = l


def load_layers():
    from models.load_util import load_named_items
    load_named_items(json_path, from_json)
