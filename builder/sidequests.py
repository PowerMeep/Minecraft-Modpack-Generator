from layers import LAYER_RESOURCEFUL, LAYER_HITMAN, LAYER_SUNBURN, LAYER_TOUGH_AS_NAILS, LAYER_INSOMNIA, LAYER_LYCANITES
from models import Sidequest


def generic_generate(source_list, players=None):
    from random import choice
    data = {}
    if players:
        for player in players:
            data[player] = choice(source_list)
    else:
        return choice(source_list)
    return data


def generate_hoarder_items(players=None):
    items = [
        'Iron',
        'Copper',
        'Diamonds',
        'Emeralds',
        'Gold'
    ]
    return generic_generate(items, players)


def generate_locations(players=None):
    locations = [
        'Treetops',
        'Cliffside',
        'Mountaintop',
        'Underwater'
    ]
    return generic_generate(locations, players)


def generate_build_prompts(players=None):
    prompts = [
        'Tower',
        'Upside-Down',
        'Spirals',
        'Natural',
        'Cubes',
        'Circles',
        'Triangles'
    ]
    return generic_generate(prompts, players)


# ------------------------------
SQ_LOCATION = Sidequest(
    name='Location, Location',
    description='Players must set up base in the given location.',
    generator=generate_locations
)

SQ_404 = Sidequest(
    name='404 Challenge',
    description=(
        'Once the sun sets on the first day,'
        ' players must go underground and never return to the surface.'
    )
)

SQ_NOMADS = Sidequest(
    name='Nomadic',
    description='Players may not construct any long-term base and must continuously travel.'
)

# ---- quests related to survival
SQ_SUNBURN = Sidequest(
    name='Not the Light!',
    description='Players must stay out of direct sunlight.',
    layers=[LAYER_SUNBURN]
)

SQ_INSOMNIA = Sidequest(
    name='Insomnia',
    description='Players are unable to sleep.',
    layers=[LAYER_INSOMNIA]
)

SQ_TOUGH_AS_NAILS = Sidequest(
    name='Tough as Nails',
    description='Players must stay at a comfortable temperature and stay hydrated.',
    layers=[LAYER_TOUGH_AS_NAILS]
)

SQ_LYCANITES = Sidequest(
    name='Like what now?',
    description='All mobs replaced with Lycanites',
    layers=[LAYER_LYCANITES]
)


# ---- quests satisfied by player deaths
SQ_AMONGUS = Sidequest(
    name='Sussy Baka',
    description=(
        'A splinter cell of players are imposters that must try to prevent the main goal.'
        ' The hard part is not getting caught!'
    ),
    requires_players=True,
    hardcore=True,
    layers=LAYER_HITMAN
)

SQ_MANHUNT = Sidequest(
    name='Manhunt',
    description=(
        'A splinter cell of players actually tries to complete the mission'
        ' while everybody else tries to stop them.'
    ),
    requires_players=True,
    hardcore=True,
    layers=LAYER_HITMAN
)

SQ_BOUNTIES = Sidequest(
    name='Bounties',
    description=(
        'A splinter cell of players actually tries to complete the mission'
        ' while everybody else tries to stop them.'
    ),
    requires_players=True,
    layers=LAYER_HITMAN
)

SQ_ALL_FOR_ONE = Sidequest(
    name='All for One',
    description='If one player dies, all other players die simultaneously.'
)


# ---------------------------------
SQ_BUILD_PROMPT = Sidequest(
    name='Feeling Inspired',
    description='Players must build something based on the given prompt.',
    generator=generate_build_prompts
)

SQ_HOARDER = Sidequest(
    name='Hoarder',
    description='Players must stockpile the given resource.',
    layers=[LAYER_RESOURCEFUL],
    generator=generate_hoarder_items
)
