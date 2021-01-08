from bs4 import BeautifulSoup as bs4
import requests
from telegram import Bot
import datetime
import pytz
import hashlib
import re
from telegram.ext import Updater, CommandHandler, JobQueue
from AstroBot import Helper
import time

indt = pytz.timezone("Asia/Kolkata")

class PhotoBot():

    def __init__(self):
        self.h = Helper()
        return
        
    def get_apod(self, context):

        #API call
        url   = "https://api.nasa.gov/planetary/apod?api_key={}".format(open('config/apod_key.conf','r').read())
        resp  = requests.get(url).json()

        try:
            url   = resp['url']
        except:
            url   = ""

        try:
            date  = "Date: " + str(resp['date'])
        except:
            date = ""

        try:
            title = "APOD - " + resp['title']
        except:
            title = "APOD"
        
        try:
            explanation = resp['explanation']
        except:
            explanation = ""

        try:
            context.bot.sendPhoto(chat_id=context.job.context, photo=url, caption = str(title+"\n\n"+explanation+"\n" + date))
        except:
            message = ("<a href=\""+url+"\"><b>" + title + "</b></a>\n\n" +"\n" +explanation+"\n<i>"+date+"</i>\n")
            context.bot.sendMessage(chat_id=context.job.context, text=message, parse_mode='HTML')
        
    
    def daily_job(self, update, context):

        job_removed= self.h.remove_job(str(update.message.chat_id), context)
        if(job_removed):
            r = context.bot.sendMessage(chat_id=update.message.chat_id, text="Running instance terminated.")
            time.sleep(10)
            context.bot.delete_message(update.message.chat_id, r.message_id)

        context.bot.sendMessage(chat_id=update.message.chat_id, text="APOD started")
        context.job_queue.run_daily(self.get_apod,time=datetime.time(11,0,0,tzinfo=indt), context=update.message.chat_id, name=str(update.message.chat_id))

   
    def stop_func(self, update, context):
        job_removed = self.h.remove_job(str(update.message.chat_id), context)
        if(job_removed):
            context.bot.sendMessage(chat_id=update.message.chat_id, text='APOD has been stopped.')


