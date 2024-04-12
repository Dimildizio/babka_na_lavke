import os
from utils import get_yaml, get_localization


CONFIG = get_yaml()
FASTAPI_BASE_URL = CONFIG['swapper']
IMAGE_DIR = CONFIG['folder']
TOKEN = CONFIG['token']
DELAY_BETWEEN_IMAGES = int(CONFIG['delay'])
MIN_AGE = int(CONFIG['min_age'])
MAX_AGE = int(CONFIG['max_age'])
MIN_FONT = int(CONFIG['min_font'])
MAX_IMGS = int(CONFIG['max_imgs'])

TG = CONFIG['tg']
TGPUBLIC = CONFIG['tgpublic']
GITHUB = CONFIG['github']
ADJUFACE = CONFIG['adjuface']
SENT_TIME = {}

TXT = get_localization(lang=CONFIG['lang'])

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)
