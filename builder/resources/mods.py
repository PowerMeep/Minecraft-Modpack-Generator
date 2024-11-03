import json

from models.mod import json_path

from flask_restful import Resource


class Mods(Resource):
    def get(self):
        with open(json_path) as f:
            return json.load(fp=f)
