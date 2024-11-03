import logging
logger = logging.getLogger()


class Sidequest:
    def __init__(self,
                 name,
                 description,
                 requires_players=False,
                 hardcore=False,
                 layers=None,
                 generator=None,
                 data=None):
        self.name = name
        self.description = description
        self.requires_players = requires_players
        self.forces_hardcore = hardcore
        self.layers = layers or []
        self.generator = generator
        self.data = None

    def generate(self,
                 players=None):
        if self.generator:
            self.data = self.generator(players)

    def to_json(self):
        out = {
            'name': self.name,
            'description': self.description
        }
        if self.data:
            out['data'] = self.data
        return out


sidequests_by_name = {}


def from_json(obj: dict):
    from models.load_util import get_layers
    m = Sidequest(
        name=obj.get('name'),
        description=obj.get('description'),
        requires_players=obj.get('requires_players'),
        hardcore=obj.get('hardcore'),
        layers=get_layers(obj.get('layers')),
        data=obj.get('data')
    )
    logger.info(f'Loaded Sidequest: {m.name}')
    sidequests_by_name[m.name] = m


def load_sidequests():
    from models.load_util import load_named_items
    load_named_items('configs/sidequests.json', from_json)
