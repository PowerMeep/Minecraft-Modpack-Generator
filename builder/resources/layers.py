import json

from models.layer import json_path

from flask_restful import Resource


class Layers(Resource):
    def get(self):
        with open(json_path) as f:
            return json.load(fp=f)
