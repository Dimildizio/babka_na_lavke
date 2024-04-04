import os
from utils import get_yaml


CONFIG = get_yaml()
FASTAPI_BASE_URL = CONFIG['swapper']
IMAGE_DIR = CONFIG['folder']
TOKEN = CONFIG['token']
DELAY_BETWEEN_IMAGES = int(CONFIG['delay'])
MIN_AGE = int(CONFIG['min_age'])
MIN_FONT = int(CONFIG['min_font'])
MAX_IMGS = int(CONFIG['max_imgs'])
GENDER_1 = CONFIG['g1']
GENDER_2 = CONFIG['g2']
GENDER_3 = CONFIG['g3']
SENT_TIME = {}


if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)
