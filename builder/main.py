import logging

import models.layer

logger = logging.getLogger()


def load():
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s'
    )
    logger.setLevel(logging.INFO)

    from models.layer import load_layers
    from models.sidequest import load_sidequests
    from models.scenario import load_scenarios
    from models.challenge import load_challenges
    from models.compat import load_compats

    load_layers()
    load_sidequests()
    load_scenarios()
    load_challenges()
    load_compats()

    for l in models.layer.layers_by_name.values():
        if l.references == 0:
            logger.warning(f'Layer "{l.name}" has no references!')

    for l in models.scenario.scenarios_by_name.values():
        if l.references == 0:
            logger.warning(f'Scenario "{l.name}" has no references!')

    for l in models.sidequest.sidequests_by_name.values():
        if l.references == 0:
            logger.warning(f'Sidequest "{l.name}" has no references!')

def start():
    import bot
    bot.start()


def main():
    load()
    start()


if __name__ == '__main__':
    main()
