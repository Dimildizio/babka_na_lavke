import json
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