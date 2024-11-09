import logging
import random

from models.layer import Layer

logger = logging.getLogger()

# RelationTypes
rt_embedded = 1
rt_optional_dep = 2
rt_required_dep = 3
rt_tool = 4
rt_incompatible = 5
rt_include = 6


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
        self.modloader = None
        self.result = Layer()
        self.sources_by_mod = {}
        self.sources_by_dep = {}
        self.meta_by_sidequest = {}

    def get_name(self):
        if self.theme:
            return f'{self.challenge.name} - {self.theme.name}'
        return self.challenge.name

    def get_combined_mods(self):
        comb = {}
        # Apply deps first so they can be overridden by local configs
        comb.update(self.sources_by_dep)
        comb.update(self.sources_by_mod)
        return comb

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
        from models.mod import Mod
        self.result.fetch_metadata()
        mods_by_version = {}
        mod: Mod
        for mod in self.result.mods:
            for version in mod.sources_by_version.keys():
                # this block would only consider the major-minor numbers
                # trimmed_version = '.'.join(version.split('.')[:2])
                # mods_by_version.setdefault(trimmed_version, set()).add(mod)
                mods_by_version.setdefault(version, set()).add(mod)

        best = None
        for version, mods in mods_by_version.items():
            # TODO: Expand this to prioritize some mods over others.
            #       For now, the score is just the number of mods supported.
            score = len(mods)
            if best is None or best[1] < score:
                best = version, score

        self.version = best[0]
        logger.info(f'Selected version {self.version}')
        for mod in self.result.mods:
            source = mod.get_best_source(self.version)
            if source:
                self.sources_by_mod[mod] = source
            else:
                logger.info(f'Dropping incompatible core mod: {mod.curseforge_id}')

        from apis import curseforge
        self.modloader = curseforge.get_recommended_modloader(self.version)
        if not self.modloader:
            logger.error(f'Unable to get a recommended loader for version {self.version}')
        else:
            logger.info(f'Selected modloader: {self.modloader}')

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
                        self.sources_by_mod[mod] = mod.get_best_source(self.version)
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

    def _get_next_deps(self,
                       temp_sources_by_mod: dict,
                       level: int = 0) -> dict:
        from models.mod import CFSource, mods_by_id, Mod
        logger.warning(f'Pulling dependencies - level {level}')

        new_sources_by_mod = {}

        source: CFSource
        for source in temp_sources_by_mod.values():
            for relation in source.dependencies:
                if relation.get('relationType') == rt_required_dep:
                    need_fetch = True

                    dep_id = relation.get('modId')
                    m = mods_by_id.get(dep_id)
                    if not m:
                        m = Mod(name=None, curseforge_id=dep_id)
                        mods_by_id[dep_id] = m
                    elif not m.is_stale():
                        need_fetch = False

                    if need_fetch:
                        m.fetch_sources()
                        m.save_sources()

                    source = m.get_best_source(self.version)
                    if not source:
                        logger.error(f'Could not find version {self.version} for project {dep_id}')
                    else:
                        new_sources_by_mod[m] = source

        if new_sources_by_mod:
            new_sources_by_mod.update(self._get_next_deps(new_sources_by_mod, level+1))

        return new_sources_by_mod

    def pull_dependencies(self):
        from models.mod import Mod, fetch_info
        self.sources_by_dep = self._get_next_deps(self.sources_by_mod)
        m: Mod
        fetch_info([m.curseforge_id for m in self.sources_by_dep.keys()])

    def generate_modlist_html(self) -> str:
        comb = self.get_combined_mods()
        out = ['<ul>']
        for mod in comb.keys():
            out.append(f'<li><a href="{mod.curseforge_meta.website_url}">{mod.curseforge_meta.display_name} (by {mod.curseforge_meta.author})</li>')
        out.append('</ul>')
        return '\n'.join(out)

    def generate_manifest_json(self) -> dict:
        comb = self.get_combined_mods()
        files = []
        for mod, source in comb.items():
            files.append({
                'projectID': mod.curseforge_id,
                'fileID': source.file_id,
                'required': True
            })

        out = {
            'minecraft': {
                'version': self.version,
                'modLoaders': [
                    {
                        'id': self.modloader,
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
        import json
        import os
        import re
        import shutil
        import time

        self.pull_dependencies()

        # create temp directory
        temp_dir = 'temp'
        build_dir = 'build'
        os.makedirs(temp_dir, 0o755, exist_ok=True)

        # create build directories
        output_name = f'{round(time.time() * 1000)}-{self.get_name()}-client'
        temp_output_dir = f'{temp_dir}/{output_name}'
        temp_output_overrides_dir = f'{temp_output_dir}/overrides'
        os.makedirs(temp_output_dir, 0o755,  False)
        os.makedirs(temp_output_overrides_dir, 0o755, False)

        # dump modlist to file
        with open(f'{temp_output_dir}/modlist.html', 'w') as f:
            f.write(self.generate_modlist_html())

        # dump manifest to file
        with open(f'{temp_output_dir}/manifest.json', 'w') as f:
            json.dump(self.generate_manifest_json(), fp=f, indent=4)

        for override in self.result.overrides:
            # If there is a mod on the list that we don't have, skip
            for mod in override.mods:
                if mod not in self.sources_by_mod:
                    continue
            # If the version doesn't match, skip
            if not re.match(override.versions, self.version):
                continue

            # Copy the override
            try:
                shutil.copytree(
                    src=f'data/overrides/{override.path}',
                    dst=temp_output_overrides_dir,
                    dirs_exist_ok=True
                )
            except:
                logger.error(f'Unable to copy override: {override.path}')
        shutil.make_archive(
            base_name=output_name,
            format='zip',
            base_dir='.',
            root_dir=temp_output_dir
        )
        os.makedirs(build_dir, 0o755, exist_ok=True)
        shutil.move(
            src=f'{output_name}.zip',
            dst=f'{build_dir}/{output_name}.zip'
        )
        shutil.rmtree(temp_output_dir)
        return f'{build_dir}/{output_name}.zip'


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
