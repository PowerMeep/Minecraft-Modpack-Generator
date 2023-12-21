from models import Challenge
from layers import *
from sidequests import *

duration_100_mc = "100 Minecraft Days (Synchronous, players must be online at the same time)"
duration_7_real = "7 Real Days (Asynchronous, players may come and go)"

random_mobs = [LAYER_NATURAL_WILDLIFE, LAYER_LYCANITES, LAYER_VANILLA]
dungeons = [LAYER_DUNGEONS_ARISE, LAYER_DUNGEON_CRAWL, LAYER_BATTLE_TOWERS, LAYER_VANILLA]


CHALLENGE_100_DAY = Challenge(
    name='100 Day Hardcore Survival',
    description='Players must try to survive the scenario to the 100 day mark.',
    duration=duration_100_mc,
    layers=[
        LAYER_ESSENTIALS,
        [
            LAYER_ALEXS_CAVES,
            LAYER_ZOMBIES,
            LAYER_SCULK_HORDE,
            LAYER_TWILIGHT_FOREST,

            LAYER_ICE_AND_FIRE,
            LAYER_ARS_NOVEAU,
            LAYER_STRATOSPHERICAL,
            LAYER_AETHER,
            LAYER_WINTER_WONDERLAND,
            LAYER_RL,
            LAYER_HIGH_SEAS
        ],
        LAYER_VANILLA_TERRAIN,
        LAYER_ALL_VILLAGES
    ],
    sidequests=[
        SQ_TOUGH_AS_NAILS,
        SQ_SUNBURN,
        SQ_ALL_FOR_ONE,
        SQ_INSOMNIA  # note that this effectively doubles the time required to reach 100 days
    ]
)

CHALLENGE_ONE_PERCENT = Challenge(
    name='The One Percent',
    description=(
        'Players have 7 days to accrue as much wealth as they can.'
        ' A vote is held on the 7th day to determine the victor.'
    ),
    duration=duration_7_real,
    layers=[
        LAYER_ESSENTIALS,
        [
            LAYER_ICE_AND_FIRE,
            # LAYER_STRATOSPHERICAL,  # Does not generate terrain below 0, that means no diamonds?
            LAYER_AETHER,
            LAYER_WINTER_WONDERLAND,
            LAYER_RL,
            LAYER_TWILIGHT_FOREST,
            LAYER_HIGH_SEAS
        ],
        LAYER_ALL_TERRAIN,
        LAYER_ALL_VILLAGES,
        random_mobs,
        dungeons,
        LAYER_RESOURCEFUL
    ],
    sidequests=[
        SQ_HOARDER,
        SQ_ALL_FOR_ONE,
        SQ_INSOMNIA
    ]
)

CHALLENGE_COBBLEMON = Challenge(
    name='Cobblemon',
    description=(
        'Players have 7 real world days to build a team of 6 pokemon.'
        ' A tournament is held on the 7th day to determine the victor.'
    ),
    duration=duration_7_real,
    layers=[
        LAYER_ESSENTIALS,
        LAYER_COBBLEMON,
        LAYER_VANILLA_TERRAIN,
        LAYER_ALL_VILLAGES
    ],
    sidequests=[]
)

CHALLENGE_RACE = Challenge(
    name='The Race',
    description=(
        'Players have 7 real world days to acquire the best mount they can find.'
        ' A race is held on the 7th day to determine the victor.'
    ),
    duration=duration_7_real,
    layers=[
        LAYER_ESSENTIALS,
        [
            LAYER_ICE_AND_FIRE,
            LAYER_STRATOSPHERICAL,
            LAYER_AETHER,
            LAYER_WINTER_WONDERLAND,
            LAYER_RL,
            LAYER_HIGH_SEAS
        ],
        LAYER_ALL_TERRAIN,
        LAYER_ALL_VILLAGES,
        LAYER_MOUNTS
    ],
    sidequests=[
        SQ_INSOMNIA,
        SQ_LYCANITES
    ]
)

CHALLENGE_BATTLE = Challenge(
    name='Battle',
    description=(
        'Players have 7 real world days to prep for a battle to the death.'
        ' A single-elimination tournament is held on the 7th day to determine the victor.'
    ),
    duration=duration_7_real,
    layers=[
        LAYER_ESSENTIALS,
        [
            LAYER_ICE_AND_FIRE,
            LAYER_AETHER,
            LAYER_ARS_NOVEAU,
            LAYER_RL
        ],
        LAYER_ALL_TERRAIN,
        LAYER_ALL_VILLAGES,
        dungeons,
        LAYER_COMBAT
    ],
    sidequests=[
        SQ_INSOMNIA,
        SQ_LYCANITES
    ]
)

CHALLENGE_BUILD_BATTLE = Challenge(
    name='Build Battle',
    description=(
        'Players have 7 real world days to build the best build they can build.'
        ' A vote is held on the 7th day to determine the victor.'
    ),
    duration=duration_7_real,
    layers=[
        LAYER_ESSENTIALS,
        LAYER_ALL_TERRAIN,
        LAYER_ALL_VILLAGES,
        LAYER_BUILDS
    ],
    sidequests=[
        SQ_BUILD_PROMPT,
        SQ_HOARDER,
        SQ_INSOMNIA,
        SQ_LYCANITES
    ]
)

CHALLENGE_MAYOR_MINE = Challenge(
    name='Mayor Mine',
    description=(
        'Players are each assigned a village and are given 7 days to clean it up.'
        ' A vote is held on the 7th day to determine the victor.'
    ),
    duration=duration_7_real,
    layers=[
        LAYER_ESSENTIALS,
        LAYER_MAYOR_MINE,
        LAYER_ALL_TERRAIN,
        LAYER_BUILDS
    ],
    sidequests=[
        SQ_BUILD_PROMPT,
        SQ_HOARDER,
        SQ_INSOMNIA,
        SQ_LYCANITES
    ]
)

CHALLENGE_CAPTURE_THE_FLAG = Challenge(
    name='Capture the Flag',
    description=(
        'Players spend 7 days building a fortress.'
        ' On the 7th day, a game of CTF is played to determine the winning team.'
    ),
    duration=duration_7_real,
    layers=[
        LAYER_ESSENTIALS,
        LAYER_BUILDS,
        LAYER_ALL_VILLAGES,
        LAYER_ALL_TERRAIN
    ],
    sidequests=[
        SQ_BUILD_PROMPT,
        SQ_SUNBURN,
        SQ_HOARDER,
        SQ_INSOMNIA,
        SQ_LYCANITES
    ]
)
