import json5 as json

from models.challenge import json_path


async def get():
    with open(json_path) as f:
        return json.load(fp=f)
