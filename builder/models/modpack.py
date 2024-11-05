import logging
import random

from models.layer import Layer

logger = logging.getLogger()


def choice(obj, default):
    if type(obj) is list and len(obj) > 0:
        return random.choice(obj)
    elif type(obj) is not list and obj is not None:
        return obj
    return default


class ModPack:
    def __init__(self):
        self.challenge = None
        self.version = None
        self.theme = None
        self.result = Layer()
        self.sources_by_mod = {}
        self.meta_by_sidequest = {}

    def get_name(self):
        if self.theme:
            return f'{self.challenge.name} - {self.theme.name}'
        return self.challenge.name

    def _select_theme(self):
        self.theme = choice(self.challenge.themes, None)
        if self.theme:
            logger.info(f'> Selected theme: {self.theme.name}')
            self._add_layer(self.theme)

    def _add_layer(self, layer):
        logger.info(f'> Adding layer: {layer.name}')
        self.result.update(other_layer=layer)

    def _collapse_layers(self):
        from models.mod import mods_by_name
        for layer in self.challenge.layers:
            if type(layer) is list:
                layer = choice(layer, None)
            self._add_layer(layer)

        self.result.terrain_mod = choice(self.result.terrain_mod, mods_by_name.get('Vanilla'))
        self.result.village_mod = choice(self.result.village_mod, mods_by_name.get('Vanilla'))
        self.result.add_mod(self.result.terrain_mod)
        self.result.add_mod(self.result.village_mod)

    def _select_loader_and_version(self):
        # TODO: consider stripping the patch version for more overlap

        from models.mod import Mod
        self.result.fetch_metadata()
        mods_by_version = {}
        mod: Mod
        for mod in self.result.mods:
            for version in mod.sources_by_version.keys():
                mods_by_version.setdefault(version, []).append(mod.name)

        best = None
        for version, mods in mods_by_version.items():
            # TODO: Expand this to prioritize some mods over others.
            #       For now, the score is just the number of mods supported.
            score = len(mods)
            if best is None or best[1] < score:
                best = version, score

        self.version = best[0]
        for mod in self.result.mods:
            if self.version in mod.sources_by_version.keys():
                self.sources_by_mod[mod] = mod.sources_by_version.get(self.version)

    def _select_sidequests(self,
                           players: list = None):
        from models import sidequest
        sidequest.fetch_metadata()

        # Step 1: weed out the sidequests that can't fit in the main quest
        compatibles = []
        sq: sidequest.Sidequest
        for sq in self.challenge.sidequests:
            if sq.is_compatible_with(self.version):
                compatibles.append(sq)

        # Step 2: choose up to 3 randomly
        chosen = 0
        for sq in compatibles:
            # Skip any per-player sidequests if we don't have at least 2 players
            if sq.players_upfront and (not players or len(players) < 2):
                continue

            # Flip a coin for whether this one is chosen
            if bool(random.getrandbits(1)):
                chosen += 1
                sq_meta = sq.generate(players)
                self.meta_by_sidequest[sq] = sq_meta
                for layer in sq.layers:
                    self._add_layer(layer)
                    for mod in layer.mods:
                        self.sources_by_mod[mod] = mod.sources_by_version.get(self.version)
                if chosen == 3:
                    break

    def collapse(self,
                 players: list = None):
        """
        Takes all layers added and collapses them into a single layer.
        Ensures only one of each of these:
        - Terrain mod
        - Village mod

        :return:
        """
        self._select_theme()
        self._collapse_layers()
        self._select_loader_and_version()
        self._select_sidequests(players)

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
                'mod': mod.curseforge_meta.display_name,
                'url': mod.curseforge_meta.website_url
            }
            mod_objs.append(mod_obj)

        return {
            'name': self.get_name(),
            'challenge': self.challenge.to_json(),
            'version': self.version,
            'sidequests': sq_objs,
            'mods': mod_objs
        }

    def pull_dependencies(self) -> str:
        # TODO: implement
        # iterate over all mod file dependencies
        # what does the number mean?
        # do these need to be stored in the same way as the others?
        pass

    def generate_modlist_html(self) -> str:
        out = ['<ul>']
        for mod in self.sources_by_mod.keys():
            out.append(f'<li><a href="{mod.curseforge_meta.website_url}">{mod.curseforge_meta.display_name} (by {mod.curseforge_meta.author})</li>')
        out.append('</ul>')
        return '\n'.join(out)

    def generate_manifest_json(self) -> dict:
        files = []
        for mod, source in self.sources_by_mod.items():
            files.append({
                'projectID': mod.curseforge_id,
                'fileID': source.file_id,
                'required': True
            })

        # TODO: need a version for the modloader
        # "forge-40.2.10"
        tokens = self.version.split('-')
        out = {
            'minecraft': {
                'version': tokens[0],
                'modLoaders': [
                    {
                        'id': tokens[1],
                        'primary': True
                    }
                ]
            },
            'manifestType': 'minecraftModpack',
            'manifestVersion': 1,
            'name': self.challenge.name,
            'version': 1,
            'author': 'buildbot',
            'files': files,
            'overrides': 'overrides'
        }

        return out

    def generate_modpack_zip(self) -> str:
        # TODO: implement
        # create temp directory
        # dump modlist to file
        # dump manifest to file
        # create overrides directory
        # copy in all overrides one at a time
        # compress final file
        # delete source directory
        # return filename
        pass


def generate(players=None) -> ModPack:
    # TODO: pass in other config and overrides here
    from random import choices
    from models.challenge import weights_by_challenge
    modpack = ModPack()
    modpack.challenge = choices(
        population=list(weights_by_challenge.keys()),
        weights=list(weights_by_challenge.values()),
        k=1
    )[0]
    logger.info(f'Chose challenge "{modpack.challenge.name}"')
    modpack.collapse(players)
    return modpack
