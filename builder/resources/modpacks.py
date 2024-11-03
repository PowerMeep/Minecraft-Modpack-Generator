from models.modpack import generate

from flask_restful import Resource, request


class Modpacks(Resource):
    def get(self):
        if request.is_json:
            body = request.json()
            players = body.get('players') or []
        else:
            players = request.args.getlist('player')
        modpack = generate(players)
        return modpack.to_json()
