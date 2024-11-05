from models.modpack import generate

from quart import request


async def get():
    if request.is_json:
        body = await request.json
        players = body.get('players') or []
    else:
        players = request.args.getlist('player')

    modpack = generate(players)

    response = request.args.get('response', str)
    if response == 'modlist':
        return modpack.generate_modlist_html()
    elif response == 'manifest':
        return modpack.generate_manifest_json()
    else:
        return modpack.to_json()
