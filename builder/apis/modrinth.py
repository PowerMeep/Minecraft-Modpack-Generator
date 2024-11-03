# This is WIP and not implemented yet
# https://docs.modrinth.com/api/
import json
import requests


main_url = 'https://api.modrinth.com/v2'
staging_url = 'https://staging-api.modrinth.com/v2'
root_url = main_url


def _make_requests(path: str,
                   params: dict):
    return requests.get(
        url=f'{root_url}/{path}',
        params=params
    )


def _search_mods():
    return _make_requests(
        path='search',
        params={}
    )


def get_project_info(project_id):
    # FIXME: this allegedly supports looking up multiple at a time,
    # but the docs don't describe how to provide multiple ids
    if type(project_id) is list:
        path = f'projects/'
        # params = {'ids': project_id}
        params = {'ids': project_id}
    else:
        path = f'project/{project_id}'
        params = {}

    return _make_requests(
        path=path,
        params=params
    )


if __name__ == '__main__':
    # search all mods
    # response = _search_mods()

    # better minecraft 4
    # response = _get_project_info('create')
    # response = _get_project_info('tinkers-construct')
    response = get_project_info(['create', 'tinkers-construct'])
    print(json.dumps(response.json(), indent=2))
