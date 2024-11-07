import logging
logger = logging.getLogger()

_layer_validation_data = {
    'name': (str, True),
    'description': (str, False),
    'mods': (list, False),
    'terrain_mod': (list, False),
    'village_mod': (list, False)
}

_override_validation_data = {
    'mods': (list, False),
    'versions': (str, False),
    'path': (str, True)
}


json_path = 'data/layers.json'


class Override:
    def __init__(self,
                 path=str,
                 mods=None,
                 versions=None):
        self.mods = mods or []
        self.versions = versions or []
        self.path = path


class Layer:
    def __init__(self,
                 name='Unnamed Layer',
                 description='A layer of mods',
                 terrain_mod=None,
                 village_mod=None,
                 mods=None,
                 overrides=None):
        self.name = name
        self.description = description
        self.terrain_mod = terrain_mod
        self.village_mod = village_mod
        self.mods = mods or []
        self.overrides = overrides or []

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
        if other_layer.terrain_mod and not self.terrain_mod:
            self.terrain_mod = other_layer.terrain_mod
        if other_layer.village_mod and not self.village_mod:
            self.village_mod = other_layer.village_mod
        for mod in other_layer.mods:
            self.add_mod(mod)
        self.overrides.extend(other_layer.overrides)

    def _cache_fetch_curseforge(self):
        from models.mod import Mod

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

        for mod in mods_by_id.values():
            mod.fetch_sources()
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


def _get_overrides(overrides, mod_name):
    if overrides is None:
        return None
    out = []
    from models.load_util import validate_type
    for obj in overrides:
        errors = validate_type(
            mod_name,
            _override_validation_data,
            obj
        )
        if errors:
            for error in errors:
                logger.error(error)
            continue

        out.append(
            Override(
                mods=obj.get('mods'),
                versions=obj.get('versions'),
                path=obj.get('path')
            )
        )
    return out


def from_json(obj: dict):
    from models.load_util import validate_type
    errors = validate_type(
        obj.get('name'),
        _layer_validation_data,
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
        mods=_get_mods(obj.get('mods')),
        overrides=_get_overrides(obj.get('overrides'), obj.get('name'))
    )
    layers_by_name[l.name] = l


def load_layers():
    from models.load_util import load_named_items
    load_named_items(json_path, from_json)
