import logging

logger = logging.getLogger()


def load():
    from models.mod import load_mods
    from models.layer import load_layers
    from models.sidequest import load_sidequests
    from models.challenge import load_challenges

    load_mods()
    load_layers()
    load_sidequests()
    load_challenges()


def start():
    from flask import Flask
    from flask_restful import Api

    from resources.modpacks import Modpacks
    from resources.mods import Mods
    from resources.layers import Layers
    from resources.sidequests import Sidequests
    from resources.challenges import Challenges

    app = Flask(__name__)
    api = Api(app)

    api.add_resource(Modpacks, '/')
    api.add_resource(Mods, '/mods')
    api.add_resource(Layers, '/layers')
    api.add_resource(Sidequests, '/sidequests')
    api.add_resource(Challenges, '/challenges')

    app.run(host='0.0.0.0', port=8000)


def main():
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s'
    )
    logger.setLevel(logging.INFO)
    load()
    start()


if __name__ == '__main__':
    main()
