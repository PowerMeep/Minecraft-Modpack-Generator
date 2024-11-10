import logging
logger = logging.getLogger()

_validation_data = {
    'name': (str, True),
    'description': (str, True),
    'duration': (str, True),
    'layers': (list, True),
    'villages': (list, False),
    'terrain': (list, False),
    'synced': (bool, False),
    'hardcore': (bool, False),
    'sidequests': (list, True),
    'scenarios': (list, False)
}

json_path = 'data/challenges.json'


class Challenge:
    def __init__(self,
                 name,
                 description,
                 duration,
                 hardcore: bool = False,
                 synced: bool = False,
                 layers: list = None,
                 villages: list = None,
                 terrain: list = None,
                 scenarios: list = None,
                 sidequests: list = None):
        self.name = name
        self.description = description
        self.duration = duration
        self.synced = synced
        self.hardcore = hardcore
        self.scenarios = scenarios or []
        self.sidequests = sidequests or []
        self.layers = layers or []
        self.villages = villages or []
        self.terrain = terrain or []

    def to_json(self) -> dict:
        return {
            'name': self.name,
            'description': self.description,
            'duration': self.duration
        }


challenges_by_name = {}
weights_by_challenge = {}


def _get_sidequests(element):
    from models.load_util import get_item
    from models.sidequest import sidequests_by_name
    return get_item(
        element=element,
        element_type='sidequest',
        store=sidequests_by_name
    )


def _get_scenarios(element):
    from models.load_util import get_item
    from models.scenario import scenarios_by_name
    return get_item(
        element=element,
        element_type='scenario',
        store=scenarios_by_name
    )


def from_json(obj: dict):
    from models.load_util import validate_type, get_layers
    errors = validate_type(
        obj.get('name'),
        _validation_data,
        obj
    )
    if errors:
        for error in errors:
            logger.error(error)
        return

    c = Challenge(
        name=obj.get('name'),
        description=obj.get('description'),
        duration=obj.get('duration'),
        synced=obj.get('synced'),
        hardcore=obj.get('hardcore'),
        layers=get_layers(obj.get('layers')),
        scenarios=_get_scenarios(obj.get('scenarios')),
        sidequests=_get_sidequests(obj.get('sidequests')),
    )
    logger.info(f'Loaded challenge: {c.name}')
    challenges_by_name[c.name] = c
    weights_by_challenge[c] = obj.get('weight')


def load_challenges():
    from models.load_util import load_named_items
    load_named_items(json_path, from_json)
