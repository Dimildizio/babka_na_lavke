import json
import os
import yaml
from typing import Dict


def get_yaml(filename='config.yaml') -> Dict[str, str]:
    """
    Get info from a YAML file.

    :return: A dictionary containing information.
    """
    with open(filename, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def get_localization(filename: str = 'localization.json', lang='ru') -> Dict[str, str]:
    """
    Get info from a json file.

    :return: A dictionary containing information.
    """
    with open(filename, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config[lang]


async def get_user_info(message):
    user = message.from_user
    info = f"{user.id} {user.username} {user.first_name} {user.last_name}"
    return info


async def savefile(image, file_path):
    dir_name, filename = os.path.split(file_path)
    new_dir = os.path.join(dir_name, 'boxes')
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    new_filename = os.path.join(new_dir, os.path.splitext(filename)[0] + '_box.png')
    try:
        image.save(new_filename, format='PNG')
        return new_filename
    except PermissionError:
        return False
