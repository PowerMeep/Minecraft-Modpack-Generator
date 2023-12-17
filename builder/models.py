def dict_to_x_list(d) -> list:
    out = []
    for v in d.values():
        out .append('x' if v else ' ')
    return out


class Mod:
    def __init__(self,
                 name,
                 forge=False,
                 fabric=False,
                 v112=False,
                 v116=False,
                 v118=False,
                 v119=False,
                 v120=False):
        self.name = name
        self.loaders = {
            'Forge': forge,
            'Fabric': fabric
        }
        self.versions = {
            '1.12': v112,
            '1.16': v116,
            '1.18': v118,
            '1.19': v119,
            '1.20': v120,
        }

    def __str__(self):
        return '{:>38}|[{}]|[{}]'.format(
            self.name,
            ', '.join(dict_to_x_list(self.loaders)),
            ','.join(dict_to_x_list(self.versions))
        )


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
        from mods import MOD_VANILLA
        if mod not in self.mods and mod != MOD_VANILLA:
            print(f'  > Adding mod: {mod.name}')
            self.mods.append(mod)

    def update(self, other_layer):
        if other_layer is None:
            return
        from layers import LAYER_VANILLA
        if other_layer == LAYER_VANILLA:
            return
        print(f'> Adding layer: {other_layer.name}')
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


class Sidequest:
    def __init__(self,
                 name,
                 description,
                 requires_players=False,
                 hardcore=False,
                 layers=None,
                 generator=None):
        self.name = name
        self.description = description
        self.requires_players = requires_players
        self.forces_hardcore = hardcore
        self.layers = layers or []
        self.generator = generator
        self.data = None

    def generate(self,
                 players=None):
        if self.generator:
            self.data = self.generator(players)

    def to_json(self):
        out = {
            'name': self.name,
            'description': self.description
        }
        if self.data:
            out['data'] = self.data
        return out


class Challenge:
    def __init__(self,
                 name,
                 description,
                 duration,
                 layers: list = None,
                 sidequests: list = None):
        self.name = name
        self.description = description
        self.duration = duration
        self.layers = layers or []
        self.sidequests = sidequests or []

    def to_json(self) -> dict:
        return {
            'name': self.name,
            'description': self.description,
            'duration': self.duration
        }


class ModPack:
    def __init__(self):
        self.challenge = None
        self.sidequests = []
        self.layers = []
        self.result = None

    def collapse(self, players=None):
        """
        Takes all layers added and collapses them into a single layer.
        Ensures only one of each of these:
        - Terrain mod
        - Village mod

        :return:
        """
        from mods import MOD_VANILLA
        import random
        result = Layer()

        for layer in self.challenge.layers:
            if type(layer) is list:
                layer = choice(layer, None)
            if layer:
                result.update(layer)

        for layer in self.layers:
            result.update(layer)

        result.terrain_mod = choice(result.terrain_mod, MOD_VANILLA)
        result.village_mod = choice(result.village_mod, MOD_VANILLA)

        result.add_mod(result.terrain_mod)
        result.add_mod(result.village_mod)

        for sq in self.challenge.sidequests:
            if bool(random.getrandbits(1)):
                sq.generate(players)
                self.sidequests.append(sq)
                for layer in sq.layers:
                    result.update(layer)

        # final step:
        #  use the same logic as the versions and loaders
        #  grab a slice of the proposed mods based on what versions/loaders they support
        #  drop the other mods

        self.result = result

    def to_json(self) -> dict:
        return {
            'challenge': self.challenge.to_json(),
            # 'loaders': self.result.get_loaders(),
            # 'versions': self.result.get_versions(),
            'sidequests': [sq.to_json() for sq in self.sidequests],
            'mods': [str(mod) for mod in self.result.mods]
        }


def choice(obj, default):
    from random import choice
    if type(obj) is list and len(obj) > 0:
        return choice(obj)
    elif type(obj) is not list and obj is not None:
        return obj
    return default
