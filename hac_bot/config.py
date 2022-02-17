import os
import sys
import json
from . import backend

def check_backend_config():
    if os.environ.get('BOT_BACKEND') == 'mongodb':
        print("Using MongoDB backend.")
    else:
        print("Using in-memory data store. This will reset on bot restart.")

try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
    BOT_ADMINS = os.environ['BOT_ADMINS'].split(',')
    ADMIN_CHAT = os.environ.get('ADMIN_CHAT', None)

    # AstroBot
    CHROMEDRIVER_PATH = os.environ['CHROMEDRIVER_PATH']
    GOOGLE_CHROME_BIN = os.environ.get('GOOGLE_CHROME_BIN', None)
    OPENWEATHER_KEY = os.environ['OPENWEATHER_KEY']
    VIRTUALEARTH_KEY = os.environ['VIRTUALEARTH_KEY']

    # PhotoBot
    APOD_KEY = os.environ['APOD_KEY']
    ASTROMETRY_KEY = os.environ['ASTROMETRY_KEY']
    
except KeyError as missing_key:
    print(f"Save {missing_key} environment variables.")
    sys.exit(1)

try:
    with open('data/dso_data.json', 'r', encoding='utf-8') as file_object:
        DSO_DATA = json.load(file_object)
except FileNotFoundError as error:
    print(error)
    sys.exit(1)

if os.environ.get('BOT_BACKEND') == 'mongodb':
    BACKEND = 1
    try:
        MONGODB_HOST = os.environ['MONGODB_HOST']  # pass MongoDB URL with username and password
        MONGODB_DB_NAME = os.environ['MONGODB_DB_NAME']
    except KeyError as missing_key:
        print("Save {} in environment variables.".format(missing_key))
        sys.exit(1)
    
    approved_groups = backend.get_approved_groups(db=MONGODB_DB_NAME)
    blacklist = backend.get_blacklist_users(db=MONGODB_DB_NAME)

else:
    BACKEND = 0
    blacklist = []
    approved_groups = []
