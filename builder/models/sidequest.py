import logging
logger = logging.getLogger()


class Sidequest:
    def __init__(self,
                 name,
                 description,
                 requires_players=False,
                 hardcore=False,
                 layers=None,
                 data=None):
        self.name = name
        self.description = description
        self.requires_players = requires_players
        self.forces_hardcore = hardcore
        self.layers = layers or []
        self.data = data

    def generate(self,
                 players: list = None):
        # TODO: implement
        #       if per-player, then players are required
        #       if data is empty, then assign players to each other
        pass

    def to_json(self):
        out = {
            'name': self.name,
            'description': self.description
        }
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
