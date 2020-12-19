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
        url = "https://apod.nasa.gov/apod/astropix.html"
        response = requests.get(url)
        page_text = bs4(response.text,'html.parser')
        date = page_text.find("p").contents[3].get_text().replace('\n','')
        url = self.get_url(page_text)
        title = self.get_title(page_text)
        explanation = re.sub("  +"," ",page_text.find_all('p')[2].get_text().replace("\n"," ").split("Tomorrow")[0].split("Explanation: ")[1])
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
    