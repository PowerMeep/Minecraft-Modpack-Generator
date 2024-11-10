import logging

logger = logging.getLogger()

_validation_data = {
    'triggers': (list, True),
    'projects': (list, True),
    'overrides': (dict, True)
}
json_path = 'data/compats.json'


class Compat:
    def __init__(self,
                 name: str,
                 triggers: list,
                 projects: list,
                 overrides: list):
        self.name = name
        self.triggers = triggers
        self.projects = projects
        self.overrides = overrides


all_compats = []


def from_json(obj):
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

    com = Compat(
        name=obj.get('name'),
        triggers=obj.get('triggers'),
        projects=obj.get('projects'),
        overrides=obj.get('overrides')
    )

    logger.info(f'Loaded Compat: {com.name}')
    all_compats.append(com)


def load_compats():
    from models.load_util import load_named_items
    load_named_items(json_path, from_json)
