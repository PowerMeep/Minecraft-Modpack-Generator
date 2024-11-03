def choice(obj, default):
    from random import choice
    if type(obj) is list and len(obj) > 0:
        return choice(obj)
    elif type(obj) is not list and obj is not None:
        return obj
    return default


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
        from models.mod import mods_by_name
        from models.layer import Layer
        import random
        result = Layer()

        for layer in self.challenge.layers:
            if type(layer) is list:
                layer = choice(layer, None)
            if layer:
                result.update(layer)

        for layer in self.layers:
            result.update(layer)

        result.terrain_mod = choice(result.terrain_mod, mods_by_name.get('Vanilla'))
        result.village_mod = choice(result.village_mod, mods_by_name.get('Vanilla'))

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
