#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from bs4 import BeautifulSoup as bs4
import requests
import json
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import datetime
import calendar
from profanity_check import predict

topics=['astronomy', 'latest+astronomy+news', 'astronomy+events','black+hole', 'space+exploration', 'hubble+space+telescope','space+observatory']


# In[2]:


def scrape(url):
    page  = requests.get(url)
    page_text = bs4(page.text,'html.parser')
    articles_text = page_text.find_all(class_ = "ZINbbc xpd O9g5cc uUPGi")
    return articles_text


# In[3]:


def get_url(url):
    #
    url = url.find('a').attrs['href'].replace('/url?q=','')
    url = url.split("&sa")[0]
    return url


# In[4]:


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


# In[5]:


def get_final_article(articles_text):
    data = []
    for i in articles_text: 
        data.append([get_url(i),get_time(i),i.find(class_ = "BNeawe vvjwJb AP7Wnd").contents[0]])
    data = sorted(data, key = lambda x: x[1])
    return(data[0][0])


# In[6]:


def get_article(keyword):
    
    #day = datetime.datetime.now().strftime("%A")
    #time = int(datetime.datetime.now().strftime("%H"))
    #if day == 'Sunday' and time == 16:
    #    keyword = topics[0]
    #elif day == 'Wednesday' and time == 16:
    #    keyword = topics[1]
    #elif day == 'Friday' and time == 16:
    #    keyword = topics[2]
    if(predict(keyword)==0):
        url = "https://www.google.com/search?q="+keyword+"&source=lnms&tbm=nws&sa=X&ved=2ahUKEwjZzKWTjv3qAhVFyzgGHeKzCf8Q_AUoAXoECBUQAw&biw=1680&bih=947"
        articles_text = scrape(url)
        return(get_final_article(articles_text))
    else:
        return("stfu")


# In[ ]:


def weekly_article(update, context):
    #get_article()
    chat_id = update.message.chat_id
    #update.message.reply_text(get_article())
    #bot.send_message(chat_id=chat_id, text=get_article())
    update.message.reply_text(get_article(str(context.args)))

def main():
    #day = datetime.datetime.now().strftime("%A")
    #time = int(datetime.datetime.now().strftime("%H"))
    
    updater = Updater('1183471904:AAENQORzTAU_mTDXfv8xJU1s3rmK1PuzlpU', use_context=True)
    dp = updater.dispatcher
    #dp.add_handler(CommandHandler('randomarticle',random_article))
    dp.add_handler(CommandHandler('about', weekly_article, pass_args=True))
    #dp.add_handler(MessageHandler(~Filters.command & Filters.text, test))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()


# In[ ]:

