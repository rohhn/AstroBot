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
from hac_bot.bot_helper import Helper
import re


indt = pytz.timezone("Asia/Kolkata")

f = open('testing/new_dso.json','r')
deep_sky_info = json.load(f)
f.close()

f = open('testing/sharpless_catalogue.json','r')
sharpless_cat = json.load(f)
f.close()


f = open('testing/abell_pn_catalogue.json','r')
abell_cat = json.load(f)
f.close()

class PhotoBot():

    def __init__(self):
        self._helper = Helper()
        self.astrometry = Astrometry()
        return

# ------------------------------------ APOD EVERYDAY -------------------------------------#
        
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
        
    
    def send_apod(self, update, context):

        job_removed= self._helper.remove_job(str(update.message.chat_id), context)
        if(job_removed):
            r = context.bot.sendMessage(chat_id=update.message.chat_id, text="Running instance terminated.")
            context.bot.delete_message(update.message.chat_id, r.message_id)

        context.bot.sendMessage(chat_id=update.message.chat_id, text="APOD started")
        context.job_queue.run_daily(self.get_apod,time=datetime.time(11,0,0,tzinfo=indt), context=update.message.chat_id, name=str(update.message.chat_id))

   
    def stop_apod(self, update, context):
        job_removed = self._helper.remove_job(str(update.message.chat_id), context)
        if(job_removed):
            context.bot.sendMessage(chat_id=update.message.chat_id, text='APOD has been stopped.')

# ------------------------------------ PLATESOLVE IMAGES -------------------------------------#

    def astrometry_check_job_status(self, jobid, count):
        if count <11:
            time.sleep(15)
            job_status = self.astrometry.get_job_status(jobid)
            if job_status['status'] == 'success':
                return True
            elif job_status['status'] == 'failure':
                return False
            else:
                return(self.astrometry_check_job_status(jobid,count+1))
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
            if update.message.photo:
                file = update.message.photo[-1].get_file()['file_path']
            else:
                if update.message.document.mime_type == 'image/jpeg' or update.message.document.mime_type == 'image/png':
                    file = update.message.document.get_file()['file_path']
                else:
                    raise Exception('non-image')
        except Exception as e:
            if str(e) == 'non-image':
                context.bot.sendMessage(chat_id=update.message.chat_id, text='Only JPEG/PNG file types supported.')
            elif str(e) == 'Timed out':
                context.bot.sendMessage(chat_id=update.message.chat_id, text='File size too large. Limit 5MB')
            else:
                context.bot.sendMessage(chat_id=update.message.chat_id, text='Systems down. Please report the error to the admins.')
            return -1

        upload_status = self.astrometry.url_upload(data={'request-json':json.dumps({'session':self.login_data['session'],'url':file, 'allow_commercial_usage':'n', 'allow_modifications':'n', 'publicly_visible':'n'})})
        if upload_status['status'] == 'success':
            bot_msg = update.message.reply_text(text="Uploaded successfully. It may take up to 3 minutes to get a result.")
            if self.check_job_creation(upload_status['subid'],1):
                submission_status = self.astrometry.get_submission_status(upload_status['subid'])
                jobid = submission_status['jobs'][0]
                bot_msg.edit_text( text="Analyzing...")
                if self.astrometry_check_job_status(jobid,1):
                    final_image = self.astrometry.get_final_image(jobid)
                    
                    bot_msg.edit_text( text="Final image ready.")
                    try:
                        job_info = self.astrometry.get_job_info(jobid)
                        self.detailed_msg = ""
                        for obj in job_info['objects_in_field']:
                            if re.search('^M ', obj):
                                obj = re.sub("M ","Messier ", obj)
                            try:
                                for t in deep_sky_info:
                                    for name in t['object name']:
                                        if name.lower() == obj.lower().strip():
                                            names = '/'.join(t['object name'])
                                            try:
                                                msg = str(names + ' is a ' + t['object type'] + ' in the constellation ' + t['constellation'] + '. ' + t['visibility'])
                                            except:
                                                msg = str(names + ' is a ' + t['object type'] + ' in the constellation ' + t['constellation'] + '. ')
                                            if re.match(msg, self.detailed_msg):
                                                msg = ""
                                            else:
                                                self.detailed_msg = self.detailed_msg + msg + '\n\n'
                                            

                            except Exception as e:
                                print('Uknown object: {}'.format(obj))
                        objects = ', '.join(job_info['objects_in_field'])
                        self.objects = "Identified objects: " + objects
                        try:
                            self.astrometry_image_msg = update.message.reply_photo(photo= final_image, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text = "List identified objects", callback_data="list_astrometry_objects")], [InlineKeyboardButton(text = "Detailed objects info", callback_data="detailed_astrometry_objects")]]))
                        except:
                            self.astrometry_image_msg = update.message.reply_text(text="Unable to fetch final image.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text = "List identified objects", callback_data="list_astrometry_objects")], [InlineKeyboardButton(text = "Detailed objects info", callback_data="detailed_astrometry_objects")]]))
                    except Exception as e:
                        print(e)
                        try:
                            update.message.reply_photo(photo= final_image)
                        except:
                            update.message.reply_text(text = 'Unable to fetch final image.')
                    return -1
                else:
                    bot_msg.edit_text(text="Unable to solve the given image.")
                    return -1
            else:
                bot_msg.edit_text(text="Job took too long. Request closed.")
                return -1
        else:
            return -1


    def timeout(self, update, context):
        self.req_msg.edit_text(text="Your request timed out. Please try again.")
        return -1 

    def start_platesolve(self, update, context):
        if update.message.chat.type == 'private' or str(update.message.chat_id) == str(open('config/test_chat.conf','r').read()):
            try:
                self.login_data = self.astrometry.login(data={'request-json': json.dumps({'apikey':open('config/astrometry_key.conf','r').read()})})
                if self.login_data['status'] == 'success':
                    self.req_msg = update.message.reply_text(text='Send me a picture to analyze.\n\nType /cancel to abort the request.')
                    return 1
                else:
                    context.bot.sendMessage(chat_id=update.message.chat_id, text='Systems down. Please report the error to the admins.')
                    return -1
            except ConnectionError:
                self.req_msg = update.message.reply_text(text='Connection error. Please try again.')
                return -1
            except:
                self.req_msg = update.message.reply_text(text='Systems down. Please report the error to the admins.')
                return -1
        else:
            self.req_msg = update.message.reply_text(text='This feature is only available in private chat with @HAC_PhotoBot')
            return -1

    def cancel(self, update, context):
        context.bot.sendMessage(chat_id = update.message.chat_id, text="Cancelled request.")
        return -1

# ------------------------------------ GET INFO ON DEEPSKY OBJECTS -------------------------------------#

    def get_dso_data(self, update, context):
        if update.message.text.lower().split('@hac_photobot tell me about')[1].strip() != '':
            search_object = update.message.text.lower().split('@hac_photobot tell me about')[1].strip()
            
            ignore_keys = ['object name', 'object type', 'constellation', 'deep_sky_image_link', 'visibility']
            cat = 1
            if re.search('m[ ]*[0-9]+', search_object.lower()):
                search_object = re.sub('m[ ]*',"Messier ", search_object.lower())
            elif re.search('messier[0-9]+', search_object.lower()):
                search_object = re.sub('messier',"Messier ", search_object.lower())
            elif re.search('ngc[0-9]+', search_object.lower()):
                search_object = re.sub('ngc',"NGC ", search_object.lower())
            elif re.search('ic[0-9]+', search_object.lower()):
                search_object = re.sub('ic',"IC ", search_object.lower())
            elif re.search('(sharpless) *2-', search_object.lower()):
                search_object = re.sub('sharpless *2-', 'sh 2-', search_object.lower())
                cat = 2
            elif re.search('(sh) *2-', search_object.lower()):
                search_object = re.sub('sh *2-', 'sh 2-', search_object.lower())
                cat = 2
            elif re.search('(sharpless) *(?!2-)', search_object.lower()):
                search_object = re.sub('sharpless *', 'sh 2-', search_object.lower())
                cat = 2
            elif re.search('(sh) *(?!2-)', search_object.lower()):
                search_object = re.sub('sh *', 'sh 2-', search_object.lower())
                cat = 2
            elif re.search('^sh ', search_object.lower()):
                cat = 2
            elif re.search('^abell[ ]*[0-9]+', search_object.lower()):
                cat = 3
                search_object = re.sub('^abell[ ]*','abell ', search_object.lower())
            print(search_object)
            try:
                self.full_detail_msg = ""
                self.dso_msg = ""
                if cat ==1:
                    for t in deep_sky_info:
                        for name in t['object name']:
                            if name.lower() == search_object.lower().strip():
                                found_object = [t]
                    if found_object:
                        for x in found_object:
                            img_link = x['deep_sky_image_link']
                            try:
                                names = '/'.join(x['object name'])
                                self.dso_msg = str(names + ' is a ' + x['object type'] + ' in the constellation ' + x['constellation'] + '. ' + x['visibility'] + '\n')
                            except:
                                self.dso_msg = str(names+ ' is a ' + x['object type'] + ' in the constellation ' + x['constellation'] + '. \n')
                            
                            for key in x:
                                if key not in ignore_keys:
                                    self.full_detail_msg += '\n' + key + ': ' + x[key]
                            update.message.reply_photo(caption=self.dso_msg, photo = img_link, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='Get detailed information', callback_data='full_dso_data')]]))
                    else:
                        msg = 'Object '+ search_object +' not found'
                        update.message.reply_text(text=msg)
                elif cat == 2:
                    x = [f for f in sharpless_cat if f.lower()==search_object.lower()]
                    if x:
                        img_link = sharpless_cat[x[0]]['deep_sky_image_link']
                        names = "/".join(sharpless_cat[x[0]]['alt_names'])
                        if names:
                            names = sharpless_cat[x[0]]['object name'] + '/' + names
                        else:
                            names = sharpless_cat[x[0]]['object name']
                        self.dso_msg = str(names + ' - ' + sharpless_cat[x[0]]['short_description'])
                        self.full_detail_msg = sharpless_cat[x[0]]['full_description']
                        update.message.reply_photo(caption=self.dso_msg, photo = img_link, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='Get detailed information', callback_data='full_dso_data')]]))
                elif cat == 3:
                    x = [f for f in abell_cat if f.lower()==search_object.lower()]
                    if x:
                        img_link = abell_cat[x[0]]['image_link']
                        name = abell_cat[x[0]]['object name']
                        description = abell_cat[x[0]]['description'].replace('PN', 'Planetary nebula')
                        for v in description.split('\n'):
                            if bool(v) & bool(re.search('^[0-9]',v)):
                                v = '<i><u>' + v + '</u></i>'
                            self.dso_msg = self.dso_msg + v + '\n'
                        self.dso_msg = str('<b>'+name+'</b>\n' + self.dso_msg)
                        html_message = f"<a href=\"{img_link}\">&#8204;</a>{str(self.dso_msg)}"
                        update.message.reply_text(text=html_message, parse_mode='HTML')
            except Exception as e:
                msg = 'Object '+ search_object +' not found'
                update.message.reply_text(text=msg)
                print(e)
        else:
            msg = 'No object entered.'
            update.message.reply_text(text=msg)


# ----------------------------------------------------------------------------------------#

    def help(self, update, context):
        #new help
        if update.message.chat.type == 'private':
            context.bot.sendMessage(chat_id=update.message.chat_id, text=self._helper.photobot_help + "\n\n/startapod - Receive daily Astronomy Picture of the Day from NASA.\n\n/stopapod - Stop receiving APOD.")


    def callback_query_handler(self, update, context):
        if update.callback_query.data == 'list_astrometry_objects':
            update.callback_query.message.edit_caption(reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="< Back", callback_data="back_astrometry")]]) ,caption=self.objects)
        if update.callback_query.data == 'detailed_astrometry_objects':
            update.callback_query.message.edit_caption(reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="< Back", callback_data="back_astrometry")]]) ,caption=self.detailed_msg)
        elif update.callback_query.data == 'back_astrometry':
            update.callback_query.message.edit_caption(reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="List identified objects", callback_data="list_astrometry_objects")], [InlineKeyboardButton(text = "Detailed objects info", callback_data="detailed_astrometry_objects")]]) ,caption="")
        elif update.callback_query.data == 'full_dso_data':
            update.callback_query.message.edit_caption(reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="< Back", callback_data="back_dso_data")]]) ,caption=self.full_detail_msg)
        elif update.callback_query.data == 'back_dso_data':
            update.callback_query.message.edit_caption(reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Get detailed information", callback_data="full_dso_data")]]) ,caption=self.dso_msg)

