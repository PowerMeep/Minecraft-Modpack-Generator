import os
import json5 as json

from models.layer import json_path


async def get():
    out = {}
    for item in os.listdir(json_path):
        path = f'{json_path}/{item}'
        if os.path.isfile(path):
            with open(path) as f:
                out.update(json.load(fp=f))
    return out
