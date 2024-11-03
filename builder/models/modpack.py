import random


def choice(obj, default):
    if type(obj) is list and len(obj) > 0:
        return random.choice(obj)
    elif type(obj) is not list and obj is not None:
        return obj
    return default


class ModPack:
    def __init__(self):
        self.challenge = None
        self.layers = []
        self.version = None
        self.sources_by_mod = {}
        self.meta_by_sidequest = {}

    def collapse(self,
                 players: list = None):
        """
        Takes all layers added and collapses them into a single layer.
        Ensures only one of each of these:
        - Terrain mod
        - Village mod

        :return:
        """
        from models.mod import mods_by_name, Mod
        from models.layer import Layer
        from models.sidequest import Sidequest
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

        # Generate sidequest metadata
        sq: Sidequest
        for sq in self.challenge.sidequests:
            if bool(random.getrandbits(1)):
                # Skip any per-player sidequests if we don't have at least 2 players
                if sq.players_upfront and (not players or len(players) < 2):
                    continue
                sq_meta = sq.generate(players)
                self.meta_by_sidequest[sq] = sq_meta
                for layer in sq.layers:
                    result.update(layer)

        # Commit to a version
        # TODO: consider stripping the patch version for more overlap
        result.fetch_metadata()

        mods_by_version = {}
        mod: Mod
        for mod in result.mods:
            for version in mod.sources.keys():
                mods_by_version.setdefault(version, []).append(mod.name)

        best = None
        for version, mods in mods_by_version.items():
            # TODO: Expand this to prioritize some mods over others.
            #       For now, the score is just the number of mods supported.
            score = len(mods)
            if best is None or best[1] < score:
                best = version, score

        self.version = best[0]
        for mod in result.mods:
            if self.version in mod.sources.keys():
                self.sources_by_mod[mod] = mod.sources.get(self.version)

    def to_json(self) -> dict:
        sq_objs = []
        for sq, meta in self.meta_by_sidequest.items():
            sq_obj = sq.to_json()
            if meta:
                sq_obj['meta'] = meta
            sq_objs.append(sq_obj)

        mod_objs = []
        for mod, source in self.sources_by_mod.items():
            mod_obj = {
                'mod': mod.name,
                'url': source
            }
            mod_objs.append(mod_obj)

        return {
            'version': self.version,
            'challenge': self.challenge.to_json(),
            'sidequests': sq_objs,
            'mods': mod_objs
        }