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

token = "1163369796:AAE1BI447fKiuDQ9RUTCUZKcS7-Ek96zlYI"
#bot = Bot(token) #photobot
group_id = "-1001331038106" #"-1001284948052"


def fetch_picture(update, context):
    chat_id = update.message.chat_id
    search_text=""
    for i in context.args:
  #     if(profanity.contains_profanity(i)):
  #         update.message.reply_text("no result")
  #         break
  #     else:
        search_text = search_text + " " + i
    search_text = search_text + "+astronomy+picture"
    url="http://www.google.com/search?q="+ search_text +"&rlz=1C5CHFA_enIN908IN908&source=lnms&tbm=isch&sa=X&ved=2ahUKEwjkxYHbzYTrAhVTSX0KHZSHDvYQ_AUoAXoECA4QAw&biw=1261&bih=914&safe=active"
    page_text = requests.get(url)
    page_text = bs4(page_text.text, 'html.parser')
    image_url = page_text.find_all(class_ ="TxbwNb")[0].find('img')['src']
    update.message.reply_photo(image_url)
    

def main():
    
    updater = Updater(token, use_context=True)
    
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('picture',fetch_picture))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
    
    
    