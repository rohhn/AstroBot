from bs4 import BeautifulSoup as bs4
import requests
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters
from datetime import datetime
import random
import re
from better_profanity import profanity
from telegram import Bot
import pytz
import time


token ='1183471904:AAHzW9eC9XIHJwJXRiyRKrJemA3WVxY_mug'
group_id = '1045695336'
ind_tz = pytz.timezone('Asia/Kolkata')
bot = Bot(token)

#
## --------------------- HELPER FUNCTIONS ------------------------#
#def scrape(url):
#    #parse html text of the google news page url
#    page  = requests.get(url)
#    page_text = bs4(page.text,'html.parser')
#    articles_text = page_text.find_all(class_ = "ZINbbc xpd O9g5cc uUPGi")
#    #create list of articles
#    return articles_text
#
#def get_article_url(url):
#    #
#    url = url.find('a').attrs['href'].replace('/url?q=','')
#    url = url.split("&sa")[0]
#    return url
#
#def get_time(i):
#    posted_time = i.find(class_ = "r0bn4c rQMQod").contents[0]
#    posted_time = posted_time.split(" ")
#    if (posted_time[1] == 'mins' or posted_time[1] == 'min'):
#        time_since = int(posted_time[0])
#    if (posted_time[1] == 'hours' or posted_time[1] == 'hour'):
#        time_since = 60 * int(posted_time[0])
#    elif (posted_time[1] == 'days' or posted_time[1] == 'day'):
#        time_since = 24*60 * int(posted_time[0])
#    elif (posted_time[1] == 'weeks' or posted_time[1] == 'week'):
#        time_since = 7*24*60* int(posted_time[0])
#    #elif (posted_time[1] == 'months' or posted_time[1] == 'month'):
#    #    time_since = 100* int(posted_time[0])
#    else:
#        time_since = 9999999
#    return(time_since)
#
## ---------------------- HELPER FUNCTIONS ------------------------#
#
## ------------- GENERATE 3 ARTICLES PER WEEK (SUNDAY, WEDNESDAY, FRIDAY) ---------------- #
#
##topics for 3 weekly articles
#weekly_topics=['astronomy', 'latest+astronomy+news', 'astronomy+events']
#
#def get_final_weekly_article(articles_text):
#    data = []
#    for i in articles_text: 
#        data.append([get_article_url(i),get_time(i),i.find(class_ = "BNeawe vvjwJb AP7Wnd").contents[0]])
#    data = sorted(data, key = lambda x: x[1])
#    return(data[0][0])
#
#
#def get_weekly_article(day):
#    if day == 'Saturday':
#        keyword = weekly_topics[0]
#    elif day == 'Wednesday':
#        keyword = weekly_topics[1]
#    elif day == 'Friday':
#        keyword = weekly_topics[2]
#        
#    url = "https://www.google.com/search?q="+keyword+"&source=lnms&tbm=nws&sa=X&ved=2ahUKEwjTi4TOw_7qAhWzyDgGHVjpAyYQ_AUoAXoECBUQAw&biw=1680&bih=948"
#    articles_text = scrape(url)
#    return(get_final_weekly_article(articles_text))

def repeat_func(context):
    context.bot.send_message(chat_id = context.job.context.messsage.chat_id, text="test")

#BOT CALLED FUNCTION
def timer_daily(update, context):
    
    context.bot.send_message(chat_id = update.message.chat_id, text="started", context=update)
    context.job_queue.run_repeating(repeat_func, 10)

# --------------------------------------------------------------------------------------------#

def main():
    
    updater = Updater(token, use_context= True)
    time_now = datetime.now().astimezone(ind_tz)
    
#    #WEEKLY ARTICLE GENERATOR TRIGGER
#    if str(time_now.strftime("%A")) == 'Saturday' and int(time_now.strftime("%H")) == 21:
#        bot.sendMessage(chat_id=group_id, text = str(time_now.strftime("%A")) +"\'s article\n\n"+get_weekly_article('Saturday'))
#    elif str(time_now.strftime("%A")) == 'Wednesday' and int(time_now.strftime("%H")) == 17:
#        bot.sendMessage(chat_id=group_id, text = str(time_now.strftime("%A")) +"\'s article\n\n"+get_weekly_article('Wednesday'))
#    elif str(time_now.strftime("%A")) == 'Friday' and int(time_now.strftime("%H")) == 17:
#        bot.sendMessage(chat_id=group_id, text = str(time_now.strftime("%A")) +"\'s article\n\n"+get_weekly_article('Friday'))
     
        
    
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('s',timer_daily))
    updater.start_polling()


if __name__ == '__main__':
    main()