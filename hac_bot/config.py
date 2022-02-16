import os
import sys


approved = []

try:
    bot_admins = os.environ['BOT_ADMINS'].split(',')
except KeyError:
    print("Save chat IDs in BOT_ADMINS environment variable.")
    sys.exit(1)
