from bs4 import BeautifulSoup as bs4
import requests
import time
from telegram import Bot
from datetime import datetime
import pytz
import hashlib
import re
from telegram.ext import Updater, CommandHandler
from better_profanity import profanity

token = "1183471904:AAHzW9eC9XIHJwJXRiyRKrJemA3WVxY_mug"


    
def fetch_picture(update, context):
    search_text=""
    for i in context.args:
        search_text = search_text + " " + i
    search_text += " astronomy"
    api_key="c999b9b0-df71-11ea-bf62-cf2a6e7f12ba"

    headers = { 'apikey': api_key }

    params = (
       ("q",search_text),
       ("tbm","isch"),
       ("device","desktop"),
       ("hl","en"),
       ("location","Manhattan,New York,United States"),
    )
    response = requests.get('https://app.zenserp.com/api/v2/search', headers=headers, params=params)
    images_dict = response.json()
    image_url = images_dict["image_results"][0]['sourceUrl']
    context.bot.sendPhoto(chat_id= update.message.chat_id, photo = image_url)
    

def main():
    
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('picture',fetch_picture))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
    
    
    