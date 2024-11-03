import logging
logger = logging.getLogger()


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

    def get_versions(self):
        mods_by_version = {}
        for mod in self.mods:
            for version in mod.versions:
                mods_by_version.setdefault(version, []).append(mod)

        return [key for key, val in mods_by_version.items() if len(val) == len(self.mods)]

    def get_loaders(self):
        mods_by_loader = {}
        for mod in self.mods:
            for loader in mod.loaders:
                mods_by_loader.setdefault(loader, []).append(mod)
        return [key for key, val in mods_by_loader.items() if len(val) == len(self.mods)]


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
    load_named_items('configs/layers.json', from_json)
