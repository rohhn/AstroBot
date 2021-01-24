from __future__ import absolute_import
from telegram.ext import Updater, CommandHandler, JobQueue
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
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

    def check_job_status(self, jobid, count):
        if count <11:
            time.sleep(15)
            job_status = self.astrometry.get_job_status(jobid)
            if job_status['status'] == 'success':
                return True
            elif job_status['status'] == 'failure':
                return False
            else:
                return(self.check_job_status(jobid,count+1))
        else:
            return False

    def check_job_creation(self, subid, count):
        if count <11:
            time.sleep(15)
            submission_status = self.astrometry.get_submission_status(subid)
            if len(submission_status['jobs']) > 0 and submission_status['jobs'][0] is not None:
                return True
            else:
                return(self.check_job_creation(subid, count+1))
        else:
            return False
    

    def platesolve(self, update, context):
        try:
            file = update.message.photo[-1].get_file()['file_path']
        except Exception as e:
            context.bot.sendMessage(chat_id=update.message.chat_id, text='Systems down. Please report the error to the admins.')
            return -1

        upload_status = self.astrometry.url_upload(data={'request-json':json.dumps({'session':self.login_data['session'],'url':file, 'allow_commercial_usage':'n', 'allow_modifications':'n', 'publicly_visible':'n'})})
        if upload_status['status'] == 'success':
            bot_msg = update.message.reply_text(text="Uploaded successfully. It may take up to 3 minutes to get a result.")
            if self.check_job_creation(upload_status['subid'],1):
                submission_status = self.astrometry.get_submission_status(upload_status['subid'])
                jobid = submission_status['jobs'][0]
                bot_msg.edit_text( text="Analyzing...")
                if self.check_job_status(jobid,1):
                    final_image = self.astrometry.get_final_image(jobid)
                    bot_msg.edit_text( text="Final image ready.")
                    try:
                        job_info = self.astrometry.get_job_info(jobid)
                        objects = ', '.join(job_info['objects_in_field'])
                        self.objects = "Identified objects: " + objects
                        self.astrometry_image_msg = update.message.reply_photo(photo= final_image, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text = "List identified objects", callback_data="listobjects")]]))
                    except Exception as e:
                        print(e)
                        context.bot.sendPhoto(chat_id = update.message.chat_id, photo= final_image)
                    return -1
                else:
                    bot_msg.edit_text(text="Unable to solve the given image.")
                    return -1
            else:
                bot_msg.edit_text(text="Job took too long. Request closed.")
                return -1
        else:
            return -1

    def callback_query_handler(self, update, context):
        #update.callback_query.message.edit_caption(reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="< Back", callback_data="og")]]) ,caption=self.objects)
        if update.callback_query.data == 'listobjects':
            #context.bot.sendMessage(chat_id=update.message.chat_id, text="in callback handler")
            update.callback_query.message.edit_caption(reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="< Back", callback_data="back")]]) ,caption=self.objects)
        elif update.callback_query.data == 'back':
            update.callback_query.message.edit_caption(reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="List identified objects", callback_data="listobjects")]]) ,caption="")

    def timeout(self, update, context):
        #context.bot.sendMessage(chat_id=update.message.chat_id, text="Your request timed out. Please try again.")
        self.req_msg.edit_text(text="Your request timed out. Please try again.")
        return -1 

    def start_platesolve(self, update, context):
        self.login_data = self.astrometry.login(data={'request-json': json.dumps({'apikey':open('config/astrometry_key.conf','r').read()})})
        if self.login_data['status'] == 'success':
            self.req_msg = update.message.reply_text(text='Send me a picture to analyze.')
            return 1
        else:
            context.bot.sendMessage(chat_id=update.message.chat_id, text='Systems down. Please report the error to the admins.')
            return -1

    def cancel(self, update, context):
        context.bot.sendMessage(chat_id = update.message.chat_id, text="Cancelled request.")
        return -1

    def help(self, update, context):
        #new help
        if update.message.chat.type == 'private':
            context.bot.sendMessage(chat_id=update.message.chat_id, text=self.h.photobot_help + "\n\n/startapod - Receive daily Astronomy Picture of the Day from NASA.\n\n/stopapod - Stop receiving APOD.")


