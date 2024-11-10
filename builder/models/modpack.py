import logging
import random

from models.layer import Layer, ProjectMeta
from models.sidequest import Sidequest
from models.scenario import Scenario, scenarios_by_name
from models.challenge import Challenge, challenges_by_name
from models.project import Project, fetch_projects

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
        self.challenge: Challenge = None
        self.scenario: Scenario = None

        self.layers_by_name = {}
        self.version = None
        self.modloader = None

        self.sources_by_mod = {}
        self.sources_by_dep = {}
        self.meta_by_sidequest = {}
        self.compats = []

    def get_name(self):
        if self.scenario:
            return f'{self.challenge.name} - {self.scenario.name}'
        return self.challenge.name

    def get_combined_mods(self):
        comb = {}
        # Apply deps first so they can be overridden by local configs
        comb.update(self.sources_by_dep)
        comb.update(self.sources_by_mod)
        return comb

    def _select_challenge(self,
                          challenge_name: str = None):
        if challenge_name:
            self.challenge = challenges_by_name.get(challenge_name)

        if not self.challenge:
            from random import choices
            from models.challenge import weights_by_challenge

            self.challenge = choices(
                population=list(weights_by_challenge.keys()),
                weights=list(weights_by_challenge.values()),
                k=1
            )[0]

        logger.info(f'Selected challenge "{self.challenge.name}"')

    def _select_scenario(self,
                         scenario_name: str = None):
        if scenario_name:
            # FIXME: this could allow an incompatible scenario to be selected
            self.scenario = scenarios_by_name.get(scenario_name)

        if not self.scenario:
            self.scenario = choice(self.challenge.scenarios, None)

        if self.scenario:
            logger.info(f'> Selected scenario: {self.scenario.name}')

    def _add_layer(self,
                   layer: Layer):
        logger.info(f'> Adding layer: {layer.name}')
        self.layers_by_name[layer.name] = layer

    def _collect_core_layers(self):
        terrains = set()
        villages = set()

        layer: Layer
        if self.scenario:
            for layer in self.scenario.layers:
                self._add_layer(layer)
            for layer in self.scenario.terrain:
                terrains.add(layer)
            for layer in self.scenario.villages:
                villages.add(layer)

        for layer in self.challenge.layers:
            self._add_layer(layer)
        for layer in self.challenge.terrain:
            terrains.add(layer)
        for layer in self.challenge.villages:
            villages.add(layer)

        if village := choice(list(villages), None):
            self._add_layer(village)

        if terrain := choice(list(terrains), None):
            self._add_layer(terrain)

    def _select_loader_and_version(self):
        project_ids = set()
        layers_by_project_id = {}
        layer: Layer
        for layer in self.layers_by_name.values():
            project_meta: ProjectMeta
            for project_meta in layer.projects_by_id.values():
                project_ids.add(project_meta.cid)
                layers_by_project_id.setdefault(project_meta.cid, []).append(layer)

        # Fetch the project data
        projects_by_id = fetch_projects(list(project_ids))

        # Get a count of which projects support which versions
        projects_by_version = {}
        project: Project
        for project in projects_by_id.values():
            for version in project.sources_by_version.keys():
                # this block would only consider the major-minor numbers
                # trimmed_version = '.'.join(version.split('.')[:2])
                # projects_by_version.setdefault(trimmed_version, set()).add(mod)
                projects_by_version.setdefault(version, set()).add(project)

        # Select the best version
        best = None
        for version, projects in projects_by_version.items():
            # TODO: Expand this to prioritize some mods over others.
            #       For now, the score is just the number of mods supported.
            score = len(projects)
            if best is None or best[1] < score:
                best = version, score

        # Remove incompatible layers
        self.version = best[0]
        logger.info(f'Selected minecraft version {self.version}')
        for cid, project in projects_by_id.items():
            source = project.get_best_source(self.version)
            if not source:
                layer: Layer
                for layer in layers_by_project_id.get(cid):
                    if layer.projects_by_id.get(cid).required:
                        del(self.layers_by_name[layer.name])
                        logger.info(f'Dropping incompatible layer: {project.curseforge_id}')

        # For any remaining layers, add the mod sources
        for layer in self.layers_by_name.values():
            for cid in layer.projects_by_id.keys():
                project = projects_by_id.get(cid)
                source = project.get_best_source(self.version)
                if source:
                    self.sources_by_mod[project] = source

        # Select the modloader
        from apis import curseforge
        self.modloader = curseforge.get_recommended_modloader(self.version)
        if not self.modloader:
            logger.error(f'Unable to get a recommended loader for version {self.version}')
        else:
            logger.info(f'Selected modloader: {self.modloader}')

    def _select_sidequests(self,
                           sidequest_names: list = None,
                           player_names: list = None):
        project_ids = set()
        eligible_sidequests = set(self.challenge.sidequests)
        sidequests_by_project_id = {}
        layer: Layer
        for sidequest in self.challenge.sidequests:
            project_meta: ProjectMeta
            if sidequest.layers:
                for layer in sidequest.layers:
                    for project_meta in layer.projects_by_id.values():
                        project_ids.add(project_meta.cid)
                        sidequests_by_project_id.setdefault(project_meta.cid, []).append(sidequest)


        # Fetch the project data
        projects_by_id = fetch_projects(list(project_ids))
        for cid, project in projects_by_id.items():
            source = project.get_best_source(self.version)
            if source is None:
                for sidequest in sidequests_by_project_id.get(cid):
                    if sidequest.requires_project_id(cid) and sidequest in eligible_sidequests:
                        eligible_sidequests.remove(sidequest)

        # Choose up to 3 randomly
        chosen = 0
        sq: Sidequest
        for sq in eligible_sidequests:
            # Skip any per-player sidequests if we don't have at least 2 players
            if sq.players_upfront and (not player_names or len(player_names) < 2):
                continue

            choose_this = False
            if sidequest_names:
                if sq.name in sidequest_names:
                    choose_this = True
            # Flip a coin for whether this one is chosen
            elif bool(random.getrandbits(1)):
                if chosen == 3:
                    break
                choose_this = True

            if choose_this:
                chosen += 1
                sq_meta = sq.generate(player_names)
                self.meta_by_sidequest[sq] = sq_meta
                for layer in sq.layers:
                    self._add_layer(layer)
                    for project_meta in layer.projects_by_id.values():
                        project = projects_by_id.get(project_meta.cid)
                        self.sources_by_mod[project] = project.get_best_source(self.version)

    def generate(self,
                 challenge_name: str = None,
                 scenario_name: str = None,
                 sidequest_names: list = None,
                 player_names: list = None):
        self._select_challenge(challenge_name)
        self._select_scenario(scenario_name)
        self._collect_core_layers()
        self._select_loader_and_version()
        self._select_sidequests(
            sidequest_names=sidequest_names,
            player_names=player_names
        )

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
            'scenario': self.scenario.to_json(),
            'version': self.version,
            'sidequests': sq_objs,
            'mods': mod_objs
        }

    def _get_next_deps(self,
                       temp_sources_by_mod: dict,
                       level: int = 0) -> dict:
        from models.project import CFSource, fetch_projects
        logger.warning(f'Pulling dependencies - level {level}')

        new_sources_by_mod = {}

        dep_ids = set()

        source: CFSource
        for source in temp_sources_by_mod.values():
            for relation in source.dependencies:
                if relation.get('relationType') == rt_required_dep:
                    dep_id = relation.get('modId')
                    dep_ids.add(dep_id)

        mods_by_id = fetch_projects(list(dep_ids))
        for dep_id, m in mods_by_id.items():
            source = m.get_best_source(self.version)
            if not source:
                logger.error(f'Could not find version {self.version} for project {dep_id}')
            else:
                new_sources_by_mod[m] = source

        if new_sources_by_mod:
            new_sources_by_mod.update(self._get_next_deps(new_sources_by_mod, level+1))

        return new_sources_by_mod

    def pull_dependencies(self):
        self.sources_by_dep = self._get_next_deps(self.sources_by_mod)

    def apply_compats(self):
        from models.compat import all_compats
        mod_ids = set(m.curseforge_id for m in self.get_combined_mods().keys())
        valid_compats = []
        for compat in all_compats:
            is_valid = True
            for project in compat.triggers:
                if project.get('project_id') not in mod_ids:
                    is_valid = False
                    break
            if is_valid:
                valid_compats.append(compat)
        new_ids = set()
        for compat in valid_compats:
            self.compats.append(compat)
            for project in compat.projects:
                new_ids.add(project.get('project_id'))

        new_projects_by_id = fetch_projects(new_ids)
        for cid, project in new_projects_by_id.items():
            source = project.get_best_source(self.version)
            if source is not None:
                self.sources_by_mod[project] = source

    def generate_modlist_html(self) -> str:
        comb = self.get_combined_mods()
        out = ['<ul>']
        for mod in comb.keys():
            out.append(f'<li><a href="{mod.curseforge_meta.website_url}">{mod.curseforge_meta.display_name} (by {mod.curseforge_meta.author})</li>')
        out.append('</ul>')
        return '\n'.join(out).encode('utf-16','surrogatepass').decode('utf-16')

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

    def _process_override(self,
                          override_name: str,
                          target_dir: str,
                          override: dict):
        for pattern, path in override.items():
            import re
            import shutil
            if not re.match(pattern, self.version):
                continue
            try:
                logger.warning(f'{override_name}({pattern}) - Copying override: {path}')
                shutil.copytree(
                    src=f'data/overrides/{path}',
                    dst=target_dir,
                    dirs_exist_ok=True
                )
            except:
                logger.error(f'{override_name} - Unable to copy override: {path}')

    def generate_modpack_zip(self) -> str:
        import json5 as json
        import os
        import shutil
        import time

        self.pull_dependencies()
        self.apply_compats()

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
            # FIXME: character encoding
            html_data = self.generate_modlist_html()
            f.write(html_data)

        # dump manifest to file
        with open(f'{temp_output_dir}/manifest.json', 'w') as f:
            json_data = self.generate_manifest_json()
            json.dump(json_data, fp=f, indent=4)


        projects_by_id = {}
        for project in self.sources_by_mod.keys():
            projects_by_id[project.curseforge_id] = project

        for layer in self.layers_by_name.values():
            for cid, project_meta in layer.projects_by_id.items():
                if cid not in projects_by_id:
                    continue
                self._process_override(
                    override_name=f'{layer.name}.{cid}',
                    override=project_meta.overrides,
                    target_dir=temp_output_overrides_dir
                )
        for compat in self.compats:
            self._process_override(
                override_name=f'Compat {compat.name}',
                override=compat.overrides,
                target_dir=temp_output_overrides_dir
            )
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


def generate(challenge_name: str = None,
             scenario_name: str = None,
             sidequest_names: list = None,
             player_names: list = None) -> ModPack:
    # TODO: pass in other config and overrides here
    modpack = ModPack()
    modpack.generate(
        challenge_name=challenge_name,
        scenario_name=scenario_name,
        sidequest_names=sidequest_names,
        player_names=player_names
    )
    return modpack
