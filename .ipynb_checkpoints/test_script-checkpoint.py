import pandas as pd
from bs4 import BeautifulSoup as bs4
import requests
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters
import datetime
import random
import re
from better_profanity import profanity
from telegram import Bot
import pytz
import time
import sys
import logging

#logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

#logger = logging.getLogger(__name__)

token ="1183471904:AAHzW9eC9XIHJwJXRiyRKrJemA3WVxY_mug"  #'1222703294:AAFtKTZoWytkkt9ZUFehhbwuUrYyzzlitUU' 
bot = Bot(token)
#message_list = os.listdir("message")


def welcome_new(update, context):
    for new_user_obj in update.message.new_chat_members:
        chat_id = update.message.chat_id
        new_usr = ""
        message="welcome "
        try:
            new_usr = '@' + new_user_obj['username']
        except:
            new_usr = new_user_obj['first_name']
    context.bot.sendMessage(chat_id, text = message+new_usr)

def main():
    updater = Updater(token, use_context= True) 
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome_new))
    updater.start_polling()
    #updater.idle()


if __name__ == '__main__':
    main()