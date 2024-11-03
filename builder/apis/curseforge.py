# Curseforge requires the developer to apply for an API key
# It appears the key is required for all operations
# https://docs.curseforge.com/rest-api/#search-mods
import json
import os

import requests

# Curseforge requires an API key
cf_url = 'https://api.curseforge.com/v1'
api_key = os.environ.get('CURSEFORGE_API_KEY')

# Cursetools lets me do this painlessly
ct_url = 'https://api.curse.tools/v1/cf'


def _make_request(path: str,
                  params: dict,
                  body: dict = None):
    if api_key:
        root_url = cf_url
        headers = {
            'Accept': 'application/json',
            'x-api-key': api_key
        }
    else:
        root_url = ct_url
        headers = {}

    if body is not None:
        return requests.post(
            url=f'{root_url}/{path}',
            params=params,
            headers=headers,
            json=body
        )
    else:
        return requests.get(
            url=f'{root_url}/{path}',
            params=params,
            headers=headers
        )


def _search_mods():
    return _make_request(
        path='mods/search',
        params={
            'gameId': 432
        },
        body=None
    )


def get_project_info(project_id):
    if type(project_id) is list:
        path = 'mods/'
        body = {
            'modIds': project_id,
            'filterPcOnly': True
        }
    else:
        path = f'mods/{project_id}'
        body = None

    return _make_request(
        path=path,
        params={},
        body=body
    )


def get_files(project_id):
    return _make_request(
        path=f'mods/{project_id}/files',
        params={},
        body=None
    )
