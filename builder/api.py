from quart import Quart, request
from resources import modpacks
from resources import layers
from resources import sidequests
from resources import scenarios
from resources import challenges
from resources import compats

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
    return await _make_call(modpacks)


@app.route('/compats', methods=['GET'])
async def compats():
    return await _make_call(compats)


@app.route('/scenarios', methods=['GET'])
async def scenarios():
    return await _make_call(scenarios)


@app.route('/layers', methods=['GET'])
async def layers():
    return await _make_call(layers)


@app.route('/sidequests', methods=['GET'])
async def sidequests():
    return await _make_call(sidequests)


@app.route('/challenges', methods=['GET'])
async def challenges():
    return await _make_call(challenges)


def start():
    app.run(host='0.0.0.0', port=8000)


if __name__ == '__main__':
    import main
    main.load()
    start()
