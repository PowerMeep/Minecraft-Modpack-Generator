# Curseforge requires the developer to apply for an API key
# It appears the key is required for all operations
# https://docs.curseforge.com/rest-api/#search-mods
import os
from typing import Optional

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


def get_files(project_id) -> list:
    """
    Returns only the Forge mods
    :param project_id:
    :return:
    """
    files = []
    index = 0
    while True:
        response = _make_request(
            path=f'mods/{project_id}/files',
            params={
                'index': index
            },
            body=None
        )
        if response.status_code != 200:
            break

        data = response.json().get('data')
        for f in data:
            if 'Forge' in f.get('gameVersions'):
                files.append(f)

        pagination = response.json().get('pagination')
        total_count = pagination.get('totalCount')
        if total_count < index + 50:
            break
        index += 50

    return files


def get_modloader_versions(version: str,
                           include_all: bool = False):
    return _make_request(
        path='minecraft/modloader',
        params={
            'version': version,
            'includeAll': include_all
        }
    )


def get_recommended_modloader(version: str) -> Optional[str]:
    response = get_modloader_versions(version)
    if response.status_code == 200:
        for loader in response.json().get('data'):
            if loader.get('recommended'):
                return loader.get('name')
    return None
