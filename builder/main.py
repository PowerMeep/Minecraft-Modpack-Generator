import json
import logging

from builder.models.modpack import ModPack


logging.basicConfig(
    format='%(message)s'
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def generate(players=None) -> ModPack:
    from random import choices
    from models.challenge import weights_by_challenge

    modpack = ModPack()
    modpack.challenge = choices(
        population=list(weights_by_challenge.keys()),
        weights=list(weights_by_challenge.values()),
        k=1
    )[0]
    logger.info(f'Chose challenge "{modpack.challenge.name}"')
    modpack.collapse(players)
    return modpack


def main():
    from models.mod import load_mods
    from models.layer import load_layers
    from models.sidequest import load_sidequests
    from models.challenge import load_challenges

    load_mods()
    load_layers()
    load_sidequests()
    load_challenges()

    modpack = generate([])
    logger.info(json.dumps(
        modpack.to_json(),
        sort_keys=True,
        indent=4,
        separators=(',', ': ')
    ))


if __name__ == '__main__':
    # TODO: launch args
    #  - players are required beforehand for the hitman stuff
    #  - ability to specify other stuff
    main()
