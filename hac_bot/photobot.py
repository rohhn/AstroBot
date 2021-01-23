from __future__ import absolute_import
from telegram.ext import Updater, CommandHandler, JobQueue
from telegram import Bot
from bs4 import BeautifulSoup as bs4
import requests
import datetime
import pytz
import time
import json
from hac_bot.astrometry import Astrometry
from hac_bot.astrobot import Helper


indt = pytz.timezone("Asia/Kolkata")

class PhotoBot():

    def __init__(self):
        self.h = Helper()
        self.astrometry = Astrometry()
        return
        
    def get_apod(self, context):

        #API call
        url   = "https://api.nasa.gov/planetary/apod?api_key={}".format(open('config/apod_key.conf','r').read())
        resp  = requests.get(url).json()
        url   = resp['url']
        date  = "Date: " + str(resp['date'])
        title = "APOD - " + resp['title']
        explanation = resp['explanation']
        #try:
        #    url   = resp['url']
        #except:
        #    url   = ""
        #try:
        #    date  = "Date: " + str(resp['date'])
        #except:
        #    date = ""
        #try:
        #    title = "APOD - " + resp['title']
        #except:
        #    title = "APOD"
        #try:
        #    explanation = resp['explanation']
        #except:
        #    explanation = ""
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

    def check_job_status(self, jobid):
        time.sleep(30)
        job_status = self.astrometry.get_job_status(jobid)
        if job_status['status'] == 'success':
            return True
        elif job_status['status'] == 'failure':
            return False
        else:
            return(self.check_job_status(jobid))

    def check_job_creation(self, subid, count):
        if count <5:
            time.sleep(30)
            submission_status = self.astrometry.get_submission_status(subid)
            if len(submission_status['jobs']) > 0 and submission_status['jobs'][0] is not None:
                return True
            else:
                return(self.check_job_creation(subid, count+1))
        else:
            return False
    

    def platesolve(self, update, context):
        try:
            file = context.bot.getFile(update.message.photo[-1].file_id)['file_path']
        except Exception as e:
            context.bot.sendMessage(chat_id=update.message.chat_id, text='Systems down. Please report the error to the admins.')
            return -1

        upload_status = self.astrometry.url_upload(data={'request-json':json.dumps({'session':self.login_data['session'],'url':file, 'allow_commercial_usage':'n', 'allow_modifications':'n', 'publicly_visible':'n'})})
        if upload_status['status'] == 'success':
            bot_msg = context.bot.sendMessage(chat_id = update.message.chat_id, text="Uploaded successfully. Please wait...")
            if self.check_job_creation(upload_status['subid'],1):
                submission_status = self.astrometry.get_submission_status(upload_status['subid'])
                jobid = submission_status['jobs'][0]
                bot_msg.edit_text( text="Analyzing...")
                if self.check_job_status(jobid):
                    final_image = self.astrometry.get_final_image(jobid)
                    job_info = self.astrometry.get_job_info(jobid)
                    objects = ', '.join(job_info['objects_in_field'])
                    objects = "Identified objects: " + objects
                    bot_msg.edit_text( text="Final image ready.")
                    context.bot.sendPhoto(chat_id = update.message.chat_id, photo= final_image, caption=objects)
                    return -1
                else:
                    bot_msg.edit_text(text="Job Failed. Please try again.")
                    return -1
            else:
                bot_msg.edit_text(text="Request timed out.")
                return -1

    def start_platesolve(self, update, context):
        self.login_data = self.astrometry.login(data={'request-json': json.dumps({'apikey':open('config/astrometry_key.conf','r').read()})})
        if self.login_data['status'] == 'success':
            context.bot.sendMessage(chat_id=update.message.chat_id, text='Send me a picture.')
            return 1
        else:
            context.bot.sendMessage(chat_id=update.message.chat_id, text='Systems down. Please report the error to the admins.')
            return -1

    def cancel(self, update, context):
        context.bot.sendMessage(chat_id = update.message.chat_id, text="Cancelled request.")
        return -1

    def help(self, update, context):
        if update.message.chat.type == 'private':
            context.bot.sendMessage(chat_id=update.message.chat_id, text='Commands for @HAC_PhotoBot:\n\n/analyze - Generate a plate-solved image.')


