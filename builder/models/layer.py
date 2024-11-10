import logging

logger = logging.getLogger()

key_name = 'name'
key_projects = 'projects'
key_project_id = 'project_id'
key_project_name = 'project_name'
key_required = 'required'
key_overrides = 'overrides'

_layer_validation_data = {
    key_name: (str, True),
    key_projects: (list, True)
}

_project_validation_data = {
    key_project_id: (int, True),
    key_project_name: (str, False),
    key_required: (bool, False),
    key_overrides: (dict, False)
}


json_path = 'data/layers'


class ProjectMeta:
    def __init__(self,
                 cid: int = None,
                 name: str = None,
                 required: bool = True,
                 overrides: dict = None):
        self.cid = cid
        self.name = name
        self.required = required
        self.overrides = overrides or {}

    def from_json(self, obj):
        self.cid = obj.get(key_project_id)
        self.name = obj.get(key_project_name)
        self.required = obj.get(key_required)
        self.overrides = obj.get(key_overrides) or {}


class Layer:
    def __init__(self,
                 name='Unnamed Layer',
                 projects=None):
        self.name = name
        self.projects_by_id = {}
        if projects:
            for p in projects:
                pm = ProjectMeta()
                pm.from_json(p)
                self.projects_by_id[pm.cid] = pm
        self.references = 0

    def __str__(self):
        return self.name


layers_by_name = {}


def from_json(obj: dict):
    from models.load_util import validate_type
    errors = validate_type(
        obj.get(key_name),
        _layer_validation_data,
        obj
    )
    if errors:
        for error in errors:
            logger.error(error)
        return

    for project in obj.get(key_projects):
        errors = validate_type(
            project.get(key_project_id),
            _project_validation_data,
            project
        )
        if errors:
            for error in errors:
                logger.error(error)
            return

    logger.info(f'Loading Layer: {obj.get(key_name)}')
    l = Layer(
        name=obj.get(key_name),
        projects=obj.get(key_projects)
    )
    layers_by_name[l.name] = l


def load_layers():
    from models.load_util import load_named_items
    import os
    for item in os.listdir(json_path):
        path = f'{json_path}/{item}'
        if os.path.isfile(path):
            load_named_items(path, from_json)
