from bs4 import BeautifulSoup as bs4
import requests
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters
import datetime
import random
import re


#Topics for random article generator
random_topics=['astronomy', 'latest+astronomy+news', 'astronomy+events','black+holes', 'space+exploration', 'hubble+space+telescope','space+observatory']

#topics for 3 weekly articles
weekly_topics=['astronomy', 'latest+astronomy+news', 'astronomy+events']



def scrape(url):
    #parse html text of the google news page url
    page  = requests.get(url)
    page_text = bs4(page.text,'html.parser')
    articles_text = page_text.find_all(class_ = "ZINbbc xpd O9g5cc uUPGi")
    #create list of articles
    return articles_text

def get_article_url(url):
    #
    url = url.find('a').attrs['href'].replace('/url?q=','')
    url = url.split("&sa")[0]
    return url


# In[174]:


def get_time(i):
    posted_time = i.find(class_ = "r0bn4c rQMQod").contents[0]
    posted_time = posted_time.split(" ")
    if (posted_time[1] == 'hours' or posted_time[1] == 'hour'):
        time_since = 0.1 * int(posted_time[0])
    elif (posted_time[1] == 'days' or posted_time[1] == 'day'):
        time_since = 1 * int(posted_time[0])
    elif (posted_time[1] == 'weeks' or posted_time[1] == 'week'):
        time_since = 10* int(posted_time[0])
    #elif (posted_time[1] == 'months' or posted_time[1] == 'month'):
    #    time_since = 100* int(posted_time[0])
    else:
        time_since = 9999
    return(time_since)


# In[175]:


def get_final_random_article(articles_text):
    data = []
    for i in articles_text: 
        data.append([get_article_url(i),i.find(class_ = "BNeawe vvjwJb AP7Wnd").contents[0]])
    data = sorted(data, key = lambda x: x[1])
    i = random.randrange(0,len(articles_text),1)
    return(data[i][0])

def get_final_weekly_article(articles_text):
    data = []
    for i in articles_text: 
        data.append([get_article_url(i),get_time(i),i.find(class_ = "BNeawe vvjwJb AP7Wnd").contents[0]])
    data = sorted(data, key = lambda x: x[1])
    return(data[0][0])


# In[176]:


def get_random_article():
    i = random.randrange(0,len(random_topics),1)
    keyword = random_topics[i]
    url = "https://www.google.com/search?q="+keyword+"&source=lnms&tbm=nws&sa=X&ved=2ahUKEwjTi4TOw_7qAhWzyDgGHVjpAyYQ_AUoAXoECBUQAw&biw=1680&bih=948"
    articles_text = scrape(url)
    return(get_final_random_article(articles_text))

def get_weekly_article():
    day = datetime.datetime.now().strftime("%A")
    time = int(datetime.datetime.now().strftime("%H"))
    if day == 'Monday': #and time == 13:
        keyword = weekly_topics[0]
    elif day == 'Wednesday': #and time == 16:
        keyword = weekly_topics[1]
    elif day == 'Friday': #and time == 16:
        keyword = weekly_topics[2]
    else:
        return("No article today.")
        
    url = "https://www.google.com/search?q="+keyword+"&source=lnms&tbm=nws&sa=X&ved=2ahUKEwjTi4TOw_7qAhWzyDgGHVjpAyYQ_AUoAXoECBUQAw&biw=1680&bih=948"
    articles_text = scrape(url)
    return(get_final_weekly_article(articles_text))

def random_article(update, context):
    #get_article()
    chat_id = update.message.chat_id
    #update.message.reply_text(get_article())
    #bot.send_message(chat_id=chat_id, text=get_article())
    update.message.reply_text(get_random_article())

def weekly_article(update, context):
    #get_article()
    chat_id = update.message.chat_id
    #update.message.reply_text(get_article())
    #bot.send_message(chat_id=chat_id, text=get_article())
    update.message.reply_text(get_weekly_article())

def main():
    updater = Updater('1183471904:AAENQORzTAU_mTDXfv8xJU1s3rmK1PuzlpU', use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('randomarticle',random_article))
    dp.add_handler(CommandHandler('newarticle', weekly_article))
    #dp.add_handler(MessageHandler(~Filters.command & Filters.text, test))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()