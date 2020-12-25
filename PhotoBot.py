from bs4 import BeautifulSoup as bs4
import requests
from telegram import Bot
import datetime
import pytz
import hashlib
import re
from telegram.ext import Updater, CommandHandler, JobQueue
from AstroBot import Helper

indt = pytz.timezone("Asia/Kolkata")

class PhotoBot():

    def __init__(self):
        self.h = Helper()
        return
        
    def get_apod(self, context):

        #KEY   = open('config/apod_key.conf','r').read()
        url   = "https://api.nasa.gov/planetary/apod?api_key={}".format(open('config/apod_key.conf','r').read())
        resp  = requests.get(url).json()
        url   = resp['url']
        date  = resp['date']
        title = resp['title']
        cprt  = resp['copyright']
        explanation = resp['explanation']

        try:
            context.bot.sendPhoto(chat_id=context.job.context, photo=url, caption = str("APOD - "+title+"\n\n"+explanation+"\nDate: " + date))
        except:
            message = ("<a href=\""+url+"\">" +"<b>APOD - " + title + "</b></a>\n\n" +"\n" +explanation+"\n<i>Date: "+date+"</i>\n")
            context.bot.sendMessage(chat_id=context.job.context, text=message, parse_mode='HTML')
            #context.bot.sendMessage(chat_id=(open('config/test_chat.conf','r').read()), text="error")
        
    
    def daily_job(self, update, context):
        job_removed= self.h.remove_job(str(update.message.chat_id), context)
        context.bot.sendMessage(chat_id=update.message.chat_id, text="APOD started")
        context.job_queue.run_daily(self.get_apod,time=datetime.time(11,0,0,tzinfo=indt), context=update.message.chat_id)

   
    def stop_func(self, update, context):
        job_removed = self.h.remove_job(str(update.message.chat_id), context)
        if(job_removed):
            context.bot.sendMessage(chat_id=update.message.chat_id, text='APOD Stopped')