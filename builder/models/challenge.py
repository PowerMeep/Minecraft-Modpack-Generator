import logging
logger = logging.getLogger()


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


def from_json(obj: dict):
    from models.load_util import get_layers
    c = Challenge(
        name=obj.get('name'),
        description=obj.get('description'),
        duration=obj.get('duration'),
        layers=get_layers(obj.get('layers')),
        sidequests=_get_sidequests(obj.get('sidequests')),
    )
    logger.info(f'Loaded challenge: {c.name}')
    challenges_by_name[c.name] = c
    weights_by_challenge[c] = obj.get('weight')


def load_challenges():
    from models.load_util import load_named_items
    load_named_items('configs/challenges.json', from_json)
