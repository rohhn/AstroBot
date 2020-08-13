#!/usr/bin/env python
# coding: utf-8

# In[114]:

from bs4 import BeautifulSoup as bs4
import requests
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext
from telegram import Bot
import re
import datetime
import pytz

topics=['astronomy', 'latest+astronomy+news', 'astronomy+events']
token = '1222703294:AAFtKTZoWytkkt9ZUFehhbwuUrYyzzlitUU'
indt = pytz.timezone("Asia/Kolkata")


def scrape(url):
    page  = requests.get(url)
    page_text = bs4(page.text,'html.parser')
    articles_text = page_text.find_all(class_ = "ZINbbc xpd O9g5cc uUPGi")
    return articles_text

def get_article_url(url):
    #
    url = url.find('a').attrs['href'].replace('/url?q=','')
    url = url.split("&sa")[0]
    return url

def get_time(i):
    posted_time = i.find(class_ = "r0bn4c rQMQod").contents[0]
    posted_time = posted_time.split(" ")
    if (posted_time[1] == 'hours' or posted_time[1] == 'hour'):
        time_since = 0.1 * int(posted_time[0])
    elif (posted_time[1] == 'days' or posted_time[1] == 'day'):
        time_since = 1 * int(posted_time[0])
    else:
        time_since = 999
    return(time_since)

def get_final_article(articles_text):
    data = []
    for i in articles_text: 
        data.append([get_article_url(i),get_time(i),i.find(class_ = "BNeawe vvjwJb AP7Wnd").contents[0]])
    data = sorted(data, key = lambda x: x[1])
    return(data[0][0])

def send_article(context):
    day = datetime.datetime.now().strftime("%A")
    #time = int(datetime.datetime.now().strftime("%H"))
    if day == 'Sunday':
        keyword = topics[0]
    elif day == 'Wednesday':
        keyword = topics[1]
    elif day == 'Thursday':
        keyword = topics[2]
        
    url = "https://www.google.com/search?q="+keyword+"&source=lnms&tbm=nws&sa=X&ved=2ahUKEwjZzKWTjv3qAhVFyzgGHeKzCf8Q_AUoAXoECBUQAw&biw=1680&bih=947"
    articles_text = scrape(url)
    context.bot.sendMessage(chat_id = context.job.context,text = get_final_article(articles_text))


def get_article(update,context):
    context.bot.sendMessage(chat_id = update.message.chat_id, text="Articles will be posted on Sunday, Wednesday and Friday.\n\n Clear Skies!")
    context.job_queue.run_daily(send_article, time = datetime.time(12,52,0,tzinfo=indt), days= (0,3,5), context = update.message.chat_id)
    
def stop_func(bot, update, job_queue):
    bot.sendMessage(chat_id=update.message.chat_id,
                      text='stopped')
    job_queue.stop()


def main():
    updater = Updater(token, use_context = True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('weekly_articles',get_article, pass_job_queue = True))
    dp.add_handler(CommandHandler('stop_weekly_articles',stop_func, pass_job_queue = True))
    #dp.add_handler(MessageHandler(~Filters.command & Filters.text, test))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()