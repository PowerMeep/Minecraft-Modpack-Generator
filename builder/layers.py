from models import Layer
from mods import *

# Special
LAYER_ESSENTIALS = Layer(
    name='Essentials',
    description='Mods that should always be present.',
    mods=[
        MOD_LOOTR,
        MOD_RANDOMIUM,
        MOD_JEI,
        MOD_CLUMPS,
        MOD_AI_IMPROVMENTS,
        MOD_CORPSE,
        MOD_ANTIQUE_ATLAS,
        MOD_FAST_LEAF_DECAY,
        MOD_SOUND_PHYSICS,
        MOD_VOICE_CHAT
    ]
)

# Terrain
LAYER_VANILLA_TERRAIN = Layer(
    name='Any Vanilla-Friendly Terrain',
    description=(
        "Any terrain-generation mod that uses only vanilla blocks"
        " and doesn't drastically change the gameplay."
    ),
    terrain_mod=[
        MOD_VANILLA,
        MOD_TERRALITH,
        MOD_TERRAFORGED,
        MOD_TECTONIC,
        MOD_WW_OO,
        MOD_MODERNBETA
    ]
)

LAYER_ALL_TERRAIN = Layer(
    name='Any Terrain',
    description='Any terrain-generation mod',
    terrain_mod=[
        MOD_BOP,
        MOD_BYG,
        MOD_WW_EE,
        MOD_STRATOSPHERICAL,
        MOD_ECOSPHERICAL,
        MOD_VANILLA,
        MOD_TERRALITH,
        MOD_TERRAFORGED,
        MOD_TECTONIC,
        MOD_WW_OO,
        MOD_MODERNBETA
    ]
)

LAYER_ALL_VILLAGES = Layer(
    name='Any Village',
    description='Any village-generation mod',
    village_mod=[
        MOD_VANILLA,
        MOD_BETTER_VILLAGES,
        MOD_CHOICETHEOREM_VILLAGES
    ]
)

# Scenarios
LAYER_AETHER = Layer(
    name='Aether',
    description='Let the Aether mod do all the heavy lifting.',
    terrain_mod=MOD_VANILLA,
    village_mod=MOD_VANILLA,
    mods=[MOD_AETHER]
)

LAYER_ARS_NOVEAU = Layer(
    name='Ars Noveau',
    mods=[
        MOD_ARS_NOVEAU
    ]
)

LAYER_ALEXS_CAVES = Layer(
    name="Alex's Caves",
    description="Let Alex's Caves do all the heavy lifting.",
    terrain_mod=MOD_VANILLA,
    mods=[MOD_ALEXS_CAVES]
)

LAYER_COBBLEMON = Layer(
    name='Cobblemon',
    description='A modpack that only allows Pokemon to spawn.',
    mods=[
        MOD_COBBLEMON,
        MOD_BAD_MOBS
    ]
)

LAYER_HIGH_SEAS = Layer(
    name='High Seas',
    description='A layer focused around the sea.',
    terrain_mod=MOD_CONTINENTS,
    mods=[
        MOD_EUREKA_SHIPS,
        MOD_VALKYRIEN_SKIES,
        # wakes
        # effective
        # physics (sea)
        MOD_UPGRADE_AQUATIC,
        MOD_QUARK,
        MOD_AQUAMIRAE,
        MOD_AQUACULTURE,
        MOD_WEATHER
    ]
)

LAYER_ICE_AND_FIRE = Layer(
    name='Ice and Fire',
    description='A layer adding dragons and crap.',
    mods=[
        # orcs?
        # epic knights?
        MOD_GOBLINS_DUNGEONS,
        MOD_GOBLIN_TRADERS,
        MOD_ICE_AND_FIRE
    ]
)

LAYER_RL = Layer(
    name="Roughin' it",
    description='A layer focused on real-world mechanics.',
    mods=[
        MOD_ALEXS_MOBS,
        MOD_EXOTIC_BIRDS,
        MOD_BAD_MOBS,
        MOD_AQUACULTURE,
        MOD_SERENE_SEASONS,
        MOD_FARMERS_DELIGHT,
        MOD_HORSE_GENETICS,
        MOD_GENETIC_ANIMALS,
        MOD_WEATHER
    ]
)

LAYER_SCULK_HORDE = Layer(
    name='Sculk Horde',
    description='A layer focused on the spreading of the sculk',
    mods=[
        MOD_SCULK_HORDE
    ]
)

LAYER_TWILIGHT_FOREST = Layer(
    name='Twilight Forest',
    description='A layer adding the Twilight Forest dimension',
    terrain_mod=[MOD_VANILLA],
    mods=[
        MOD_TWILIGHT_FOREST
    ]
)

LAYER_WINTER_WONDERLAND = Layer(
    name='Winter Wonderland',
    description='A layer focused on snow and ice and Christmas.',
    mods=[
        MOD_PRIMAL_WINTER,
        MOD_SNOW_UNDER_TREES,
        MOD_SNOW_REAL_MAGIC,
        MOD_SNOWBALLS_FREEZE_MOBS,
        MOD_HEAD_IN_CLOUDS,
        MOD_SNOWY_SPIRITS,
        MOD_RARE_ICE,
        MOD_RAVEN_COFFEE,
        # physics (snow?)
        MOD_SPAWN_ANIMATIONS
    ]
)

LAYER_STRATOSPHERICAL = Layer(
    name='Stratospherical',
    description='A layer focusing on height and verticality.',
    terrain_mod=MOD_STRATOSPHERICAL,
    mods=[
        MOD_GRAPPLING_HOOKS,
        MOD_EUREKA_SHIPS,
        MOD_VALKYRIEN_SKIES
    ]
)

LAYER_MAYOR_MINE = Layer(
    name='Mayor Mine',
    description='A layer focusing on enhancing villages by hand.',
    village_mod=MOD_VANILLA,
    mods=[
        MOD_WAYSTONES,
        MOD_VILLAGE_NAMES,
        MOD_VILLAGER_NAMES,
        MOD_TORCHMASTER,
        MOD_BOUNTIFUL,
        MOD_VILLAGE_SPAWN
    ]
)

LAYER_ZOMBIES = Layer(
    name='Zombies',
    description='A layer focusing on zombie hordes.',
    terrain_mod=LAYER_VANILLA_TERRAIN.terrain_mod,
    mods=[
        MOD_ZOMBIE_AWARENESS,
        MOD_THE_HORDES,
        MOD_SUNSCREEN,
        MOD_DROPS,
        MOD_BAD_MOBS  # (zombies only)
        # tissous zombie pack
    ]
)


# more layers
LAYER_TOUGH_AS_NAILS = Layer(
    name='Tough as Nails',
    mods=(
        MOD_TOUGH_AS_NAILS,
        MOD_ARMOR_UNDERWEAR
    )
)

LAYER_COMBAT = Layer(
    name='Combat',
    mods=[
        MOD_BETTER_COMBAT,
        MOD_COMBAT_ROLL,
        MOD_SPARTAN_WEAPONS
    ]
)

LAYER_HITMAN = Layer(
    name='Hitman',
    mods=[
        MOD_PLAYER_COMPASS,
        MOD_MORPH,
        MOD_HIDDEN_NAMES
    ]
)

LAYER_MOUNTS = Layer(
    name='Mounts',
    mods=[
        MOD_HORSE_GENETICS,
        MOD_LASSOS,
        MOD_CRAFTABLE_SADDLES
    ]
)

LAYER_BUILDS = Layer(
    name='Builds',
    mods=[
        MOD_NATURES_COMPASS,
        MOD_CONSTRUCTION_WANDS,
        MOD_HANDCRAFTED,
        MOD_DECORATIVE_BLOCKS,
        MOD_SUPPLEMENTARIES
    ]
)

LAYER_RESOURCEFUL = Layer(
    name='Resourceful',
    mods=[
        MOD_BACKPACKS,
        MOD_TINKERS,
        MOD_CREATE,
        MOD_MYSTICAL_AGRICULTURE,
        MOD_STORAGE_DRAWERS,
        MOD_CURIOS
    ]
)

LAYER_NATURAL_WILDLIFE = Layer(
    name='Natural Wildlife',
    mods=[
        MOD_ALEXS_MOBS,
        MOD_EXOTIC_BIRDS,
        MOD_BAD_MOBS,
        MOD_AQUACULTURE
    ]
)

LAYER_LYCANITES = Layer(
    name='Lycanites',
    description='Replace all mobs with Lycanites',
    mods=[
        MOD_BAD_MOBS,
        MOD_LYCANITES
    ]
)

LAYER_VANILLA = Layer(
    name='Vanilla',
    description='Placeholder to not add any mod',
    mods=[]
)

LAYER_SUNBURN = Layer(
    name='Burn in the Sun',
    mods=[MOD_SUNBURN]
)

LAYER_DARKNESS = Layer(
    name='True Darkness',
    mods=[MOD_DARKNESS]
)

LAYER_INSOMNIA = Layer(
    name='Insomnia',
    mods=[MOD_INSOMNIA]
)

LAYER_DUNGEON_CRAWL = Layer(
    name='Dungeon Crawl',
    mods=[MODS_DUNGEON_CRAWL]
)

LAYER_DUNGEONS_ARISE = Layer(
    name='Dungeons Arise',
    mods=[MOD_DUNGEONS_ARISE]
)

LAYER_YUNGS_DUNGEONS = Layer(
    name="Yung's Dungeons",
    mods=[MOD_YUNGS_DUNGEONS]
)

LAYER_BATTLE_TOWERS = Layer(
    name='Battle Towers',
    mods=[MOD_BATTLE_TOWERS]
)


ALL_LAYERS = [layer for layer in globals() if layer.startswith('LAYER')]
