from bs4 import BeautifulSoup as bs4
import requests
from telegram import Bot
import datetime
import pytz
import hashlib
import re
from telegram.ext import Updater, CommandHandler, JobQueue

indt = pytz.timezone("Asia/Kolkata")

class PhotoBot():

    def __init__(self):
        return

    def get_url(self, page_text):
        if(page_text.find('img')):
            url = "https://apod.nasa.gov/apod/"+page_text.find_all('center')[0].find('img')['src']
            return(url)
        elif(page_text.find('iframe')):
            url = page_text.find_all('center')[0].find('iframe')['src']
            return url
        
    def get_title(self, page_text):
        if(page_text.find('img')):
            return(re.sub("  +"," ",page_text.find_all('center')[1].get_text().replace("\n"," ").split("Image")[0]))
        elif(page_text.find('iframe')):
            return(re.sub("  +"," ",page_text.find_all('center')[1].get_text().replace("\n"," ").split("Video")[0]))
        
    def sendmessage(self, context):
        
        # SECURITY WARNING store this key in a config file
        KEY   = '9qcwj5VYVjWD1qeTDzezV4CMHmMCWp7t9Lby9B7j'
        url   = "https://api.nasa.gov/planetary/apod?api_key={}".format(API_KEY)
        r     = requests.get(url)
        resp  = r.json()
        url   = resp['url']
        date  = resp['date']
        title = resp['title']
        cprt  = resp['copyright']
        explanation = resp['explanation']
        page_text = bs4(response.text,'html.parser')
        
        # Remove this conditional if not needed
        if(page_text.find('img')):
            try:
                context.bot.sendPhoto(chat_id=context.job.context, photo=url, caption = str("APOD - "+title+"\n\n"+explanation+"\nDate: " + date))
            except:
                message = ("<a href=\""+url+"\">" +"<b>APOD - " + title + "</b></a>\n\n" +"\n" +explanation+"\n<i>Date: "+date+"</i>\n")
                context.bot.sendMessage(chat_id=context.job.context, text=message, parse_mode='HTML')
        elif(page_text.find('iframe')):
            message = ("<a href=\""+url+"\">" +"<b>APOD - " + title + "</b></a>\n\n" +"\n" +explanation+"\n<i>Date: "+date+"</i>\n")
            context.bot.sendMessage(chat_id=context.job.context, text=message, parse_mode='HTML')
        return()
        
    
    def daily_job(self, update, context):
        context.bot.sendMessage(chat_id=update.message.chat_id, text="APOD started")
        context.job_queue.run_daily(self.sendmessage,time=datetime.time(11,0,0,tzinfo=indt), context=update.message.chat_id)
        #job_queue.run_repeating(testing, 10, context=update)
    
    def stop_func(self, update, context):
        context.bot.sendMessage(chat_id=update.message.chat_id, text='APOD stopped')
        context.job_queue.schedule_removal()
    
