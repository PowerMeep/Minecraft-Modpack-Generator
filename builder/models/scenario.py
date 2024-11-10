import logging

logger = logging.getLogger()

_validation_data = {
    'name': (str, True),
    'description': (str, True),
    'terrain': (list, True),
    'villages': (list, True),
    'layers': (list, True)
}
json_path = 'data/scenarios.json'


class Scenario:
    def __init__(self,
                 name: str,
                 description: str,
                 terrain: list,
                 villages: list,
                 layers: list):
        self.name = name
        self.description = description
        self.terrain = terrain
        self.villages = villages
        self.layers = layers
        self.references = 0

    def to_json(self):
        return {
            'name': self.name,
            'description': self.description
        }

scenarios_by_name = {}


def from_json(obj):
    from models.load_util import get_layers, validate_type
    errors = validate_type(
        obj.get('name'),
        _validation_data,
        obj
    )
    if errors:
        for error in errors:
            logger.error(error)
        return

    scn = Scenario(
        name=obj.get('name'),
        description=obj.get('description'),
        terrain=get_layers(obj.get('terrain')),
        villages=get_layers(obj.get('villages')),
        layers=get_layers(obj.get('layers')),
    )

    logger.info(f'Loaded Scenario: {scn.name}')
    scenarios_by_name[scn.name] = scn


def load_scenarios():
    from models.load_util import load_named_items
    load_named_items(json_path, from_json)
