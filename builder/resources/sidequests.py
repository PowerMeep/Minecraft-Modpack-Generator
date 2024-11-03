import json

from models.sidequest import json_path

from flask_restful import Resource


class Sidequests(Resource):
    def get(self):
        with open(json_path) as f:
            return json.load(fp=f)
