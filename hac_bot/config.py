import os
import sys
import json
import datetime
import pytz
from . import backend

TIMEZONE = pytz.timezone("Asia/Kolkata")
APOD_TIME = datetime.time(11, 0, 0, tzinfo=TIMEZONE)


def check_backend_config():
    if os.environ.get('BOT_BACKEND') == 'mongodb':
        print("Using MongoDB backend.")
    elif os.environ.get('BOT_BACKEND') == 'atlas_api':
        print("Using MongoDB Atlas API for backend.")
    else:
        print("Using in-memory data store. This will reset on bot restart.")

# Check if all different config variables are setup correctly
try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
    BOT_ADMINS = os.environ['BOT_ADMINS'].split(',')
    ADMIN_CHAT = os.environ.get('ADMIN_CHAT', None)
    BOT_BACKEND = os.environ.get('BOT_BACKEND', None)

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

if BOT_BACKEND == 'mongodb':
    BACKEND = 1
    try:
        MONGODB_HOST = os.environ['MONGODB_HOST']  # pass MongoDB URL with username and password
        MONGODB_PORT = os.environ['MONGODB_PORT']
        MONGODB_DB_NAME = os.environ['MONGODB_DB_NAME']
    except KeyError as missing_key:
        print("Save {missing_key} in environment variables.")
        sys.exit(1)

    approved_groups = backend.get_approved_groups(db_name=MONGODB_DB_NAME)
    blacklist = backend.get_blacklist_users(db_name=MONGODB_DB_NAME)

if BOT_BACKEND == 'atlas_api':
    BACKEND = 1
    try:
        MONGODB_API_URL = os.environ['MONGODB_API_URL']
        MONGODB_API_KEY = os.environ['MONGODB_API_KEY']
        MONGODB_DB_NAME = os.environ['MONGODB_DB_NAME']
        MONGODB_DATA_SOURCE = os.environ['MONGODB_DATA_SOURCE']
    except KeyError as missing_key:
        print(f"Save {missing_key} in environment variables.")
        sys.exit(1)

    approved_groups = backend.get_approved_groups(db_name=MONGODB_DB_NAME)
    blacklist = backend.get_blacklist_users(db_name=MONGODB_DB_NAME)
else:
    BACKEND = 0
    blacklist = []
    approved_groups = []
