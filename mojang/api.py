import requests


def get_uuid(username: str):
    """
    Convert username to UUID

    :param username: current minecraft username
    :return: full object from API
    """
    resp = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{username}')
    if resp.status_code == 200:
        return resp.json()


def name_history(uuid: str):
    """
    Get history of this UUID

    :param uuid: Mojang UUID
    :return: full list of name objects from API
    """
    resp = requests.get(f'https://api.mojang.com/user/profiles/{uuid}/names')
    if resp.ok:
        return resp.json()
