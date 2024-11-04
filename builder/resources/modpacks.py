from models.modpack import generate

from quart import request


async def get():
    if request.is_json:
        body = await request.json
        players = body.get('players') or []
    else:
        players = request.args.getlist('player')
    modpack = generate(players)
    return modpack.to_json()
