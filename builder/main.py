import json

from challenges import *
from models import ModPack

challenges = {
    CHALLENGE_100_DAY: 50,
    CHALLENGE_ONE_PERCENT: 10,
    CHALLENGE_BATTLE: 10,
    CHALLENGE_BUILD_BATTLE: 10,
    CHALLENGE_CAPTURE_THE_FLAG: 10,
    CHALLENGE_COBBLEMON: 10,
    CHALLENGE_MAYOR_MINE: 10,
    CHALLENGE_RACE: 10,
}


def generate(players=None) -> ModPack:
    from random import choices

    modpack = ModPack()
    modpack.challenge = choices(
        population=list(challenges.keys()),
        weights=list(challenges.values()),
        k=1
    )[0]
    print(f'Chose challenge "{modpack.challenge.name}"')
    modpack.collapse(players)
    return modpack


def main():
    modpack = generate([
        'ben',
        'celeste',
        'lindsey',
        'joey',
        'alex'
    ])
    print(json.dumps(
        modpack.to_json(),
        # sort_keys=True,
        indent=4,
        separators=(',', ': ')
    ))


if __name__ == '__main__':
    # TODO: launch args
    #  - players are required beforehand for the hitman stuff
    main()
