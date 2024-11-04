import logging
logger = logging.getLogger()


def load():
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s'
    )
    logger.setLevel(logging.INFO)

    from models.mod import load_mods
    from models.layer import load_layers
    from models.sidequest import load_sidequests
    from models.challenge import load_challenges

    load_mods()
    load_layers()
    load_sidequests()
    load_challenges()


def start():
    import bot
    bot.start()


def main():
    load()
    start()


if __name__ == '__main__':
    main()
