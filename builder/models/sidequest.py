import logging
from random import choice, choices

logger = logging.getLogger()

_validation_data = {
    'name': (str, True),
    'description': (str, True),
    'per_player': (bool, True),
    'players_upfront': (bool, True),
    'hardcore': (bool, False),
    'data': (dict, False),
    'layers': (list, False),
}

json_path = 'data/sidequests.json'


class Sidequest:
    def __init__(self,
                 name,
                 description,
                 per_player=False,
                 players_upfront=False,
                 hardcore=False,
                 layers=None,
                 data=None):
        self.name = name
        self.description = description
        self.per_player = per_player
        self.players_upfront = players_upfront
        self.forces_hardcore = hardcore
        self.layers = layers or []
        self.data = data
        self.references = 0

    def requires_project_id(self, project_id):
        for layer in self.layers:
            if (meta := layer.projects_by_id.get(project_id)) is not None:
                if meta.required:
                    return True
        return False

    def generate(self,
                 players: list = None):
        # If this isn't a per-player sidequest, just choose from data
        if not self.per_player:
            if not self.data:
                return None
            else:
                return choices(
                    population=list(self.data.keys()),
                    weights=list(self.data.values()),
                    k=1
                )[0]

        # If players were provided, perform per-player assignments
        assignments = {}
        sources = self.data
        if players:
            if self.data:
                # assign each player to a data using the given weights
                for player in players:
                    assignment = choices(
                        population=list(self.data.keys()),
                        weights=list(self.data.values()),
                        k=1
                    )[0]
                    assignments[player] = assignment
            elif self.data is None:
                # assign each player to another player
                sources = 'players'
                targets = set(players)
                for player in players:
                    # don't allow a player to choose themselves
                    player_in_targets = player in targets
                    if player_in_targets:
                        targets.remove(player)

                    # choose from remaining
                    target = choice(list(targets))
                    targets.remove(target)
                    assignments[player] = target

                    # re-add player if they were removed
                    if player_in_targets:
                        targets.add(player)
            else:
                return None

        return {
            'sources': sources,
            'assignments': assignments
        }

    def to_json(self):
        out = {
            'name': self.name,
            'description': self.description
        }
        return out


sidequests_by_name = {}


def from_json(obj: dict):
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

    if not obj.get('enabled'):
        logger.info(f'Skipping disabled sidequest: {obj.get('name')}')
        return

    sq = Sidequest(
        name=obj.get('name'),
        description=obj.get('description'),
        per_player=obj.get('per_player'),
        players_upfront=obj.get('players_upfront'),
        hardcore=obj.get('hardcore'),
        layers=get_layers(obj.get('layers')),
        data=obj.get('data')
    )

    logger.info(f'Loaded Sidequest: {sq.name}')
    sidequests_by_name[sq.name] = sq


def load_sidequests():
    from models.load_util import load_named_items
    load_named_items(json_path, from_json)
