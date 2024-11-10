from quart import Quart, request
from resources import modpacks as mp
from resources import layers as l
from resources import sidequests as sq
from resources import scenarios as s
from resources import challenges as c

app = Quart(__name__)


async def _make_call(mod):
    method_name = request.method.lower()
    if method := getattr(mod, method_name):
        return await method()
    else:
        print(f'no has {method_name}')
        return {}


@app.route('/', methods=['GET'])
async def modpacks():
    return await _make_call(mp)


@app.route('/scenarios', methods=['GET'])
async def mods():
    return await _make_call(s)


@app.route('/layers', methods=['GET'])
async def layers():
    return await _make_call(l)


@app.route('/sidequests', methods=['GET'])
async def sidequests():
    return await _make_call(sq)


@app.route('/challenges', methods=['GET'])
async def challenges():
    return await _make_call(c)


def start():
    app.run(host='0.0.0.0', port=8000)


if __name__ == '__main__':
    import main
    main.load()
    start()
