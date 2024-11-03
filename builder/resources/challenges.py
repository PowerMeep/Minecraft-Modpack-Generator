import json

from models.challenge import json_path

from flask_restful import Resource


class Challenges(Resource):
    def get(self):
        with open(json_path) as f:
            return json.load(fp=f)
