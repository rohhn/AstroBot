from bs4 import BeautifulSoup as bs4
import requests
import time
from telegram import Bot
import datetime
import pytz
import hashlib
import re
from telegram.ext import Updater, CommandHandler, JobQueue
from better_profanity import profanity

token = "1183471904:AAHzW9eC9XIHJwJXRiyRKrJemA3WVxY_mug"

indt = pytz.timezone("Asia/Kolkata")

def get_url(page_text):
    if(page_text.find('img')):
        url = "https://apod.nasa.gov/apod/"+page_text.find_all('center')[0].find('img')['src']
        return(url)
    elif(page_text.find('iframe')):
        url = page_text.find_all('center')[0].find('iframe')['src']
        return url
    
def get_title(page_text):
    if(page_text.find('img')):
        return(re.sub("  +","",page_text.find_all('center')[1].get_text().replace("\n","").split("Image")[0]))
    elif(page_text.find('iframe')):
        return(re.sub("  +","",page_text.find_all('center')[1].get_text().replace("\n","").split("Video")[0]))
    
def sendmessage(bot,job):
    url = "https://apod.nasa.gov/apod/astropix.html"
    response = requests.get(url)
    page_text = bs4(response.text,'html.parser')
    date = page_text.find("p").contents[3].get_text().replace('\n','')
    url = get_url(page_text)
    title = get_title(page_text)
    explanation = page_text.find_all('p')[2].get_text().replace("\n","").split("Tomorrow")[0].split("Explanation: ")[1]
    if(page_text.find('img')):
        bot.sendPhoto(chat_id=job.context.message.chat_id, photo=url, caption = str("APOD: "+title+"\n\n"+explanation+"\nDate: " + date))
    elif(page_text.find('iframe')):
        message = ("<a href=\""+url+"\">" +"<b>Astronomy Picture of the Day</b></a>\n\n" +"\n" +explanation+"\n<i>Date: "+date+"</i>\n")
        bot.sendMessage(chat_id=job.context.message.chat_id, text=message, parse_mode='HTML')
    return()
    

def daily_job(bot, update, job_queue):
    bot.sendMessage(chat_id=update.message.chat_id, text="started")
    job_queue.run_daily(sendmessage,time=datetime.time(11,23,0,tzinfo=indt), context=update)

def stop_func(bot, update, job_queue):
    bot.sendMessage(chat_id=update.message.chat_id,
                      text='stopped')
    job_queue.stop()

def main():
    updater = Updater(token)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('startapod', daily_job, pass_job_queue=True))
    dp.add_handler(CommandHandler('stopapod', stop_func, pass_job_queue=True))
    updater.start_polling()
    
if __name__ == '__main__':
    main()