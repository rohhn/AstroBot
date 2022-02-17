import re
import datetime
import pytz
import time
import requests
from telegram.ext import CallbackContext
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from hac_bot import admin_functions
from . import common_functions, astrometry, utils, config


class PhotoBot():

# ------------------------------------ APOD EVERYDAY -------------------------------------#

    @utils.is_not_blacklist
    @utils.is_approved
    def get_apod(self, context):

        #API call
        url   = f"https://api.nasa.gov/planetary/apod?api_key={config.APOD_KEY}"
        resp  = requests.get(url).json()
        url   = resp['url']
        date  = "Date: " + str(resp['date'])
        title = "APOD - " + resp['title']
        explanation = resp['explanation']
        try:
            context.bot.sendPhoto(chat_id=context.job.context, photo=url, caption = str(f"{title}\n\n{explanation}\n{date}"))
        except:
            message = (f"<a href=\"{url}\"><b>{title}</b></a>\n\n\n{explanation}\n<i>{date}</i>\n")
            context.bot.sendMessage(chat_id=context.job.context, text=message, parse_mode='HTML')

    @utils.is_not_blacklist
    @utils.is_approved
    @utils.is_group_admin
    def send_apod(self, update: Update, context: CallbackContext):

        job_removed= common_functions.remove_job(str(update.message.chat_id), context)
        if(job_removed):
            r = context.bot.sendMessage(chat_id=update.message.chat_id, text="Running instance terminated.")
            context.bot.delete_message(update.message.chat_id, r.message_id)

        context.bot.sendMessage(chat_id=update.message.chat_id, text="APOD started")
        context.job_queue.run_daily(self.get_apod,time=config.APOD_TIME, context=update.message.chat_id, name=str(update.message.chat_id))

    @utils.is_not_blacklist
    @utils.is_approved
    @utils.is_group_admin
    def stop_apod(self, update: Update, context: CallbackContext):
        job_removed = common_functions.remove_job(str(update.message.chat_id), context)
        if(job_removed):
            context.bot.sendMessage(chat_id=update.message.chat_id, text='APOD has been stopped.')

# ------------------------------------ PLATESOLVE IMAGES -------------------------------------#

    def astrometry_check_job_status(self, jobid, count=1):
        if count <11:
            time.sleep(15)
            job_status = astrometry.get_job_status(jobid)
            if job_status['status'] == 'success':
                return True
            elif job_status['status'] == 'failure':
                return False
            else:
                return(self.astrometry_check_job_status(jobid,count+1))
        return None

    def check_job_creation(self, subid, count=1):
        if count <11:
            time.sleep(15)
            submission_status = astrometry.get_submission_status(subid)
            if len(submission_status['jobs']) > 0 and submission_status['jobs'][0] is not None:
                return True
            else:
                return(self.check_job_creation(subid, count+1))
        return False

    @utils.is_not_blacklist
    @utils.is_approved
    def platesolve(self, update: Update, context: CallbackContext):
        try:
            if update.message.photo:
                image_url = update.message.photo[-1].get_file()['file_path']
            else:
                if update.message.document.mime_type == 'image/jpeg' or update.message.document.mime_type == 'image/png':
                    image_url = update.message.document.get_file()['file_path']
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

        upload_status = astrometry.url_upload(image_url, self.login_data)
        if upload_status['status'] == 'success':
            bot_msg = update.message.reply_text(text="Uploaded successfully. It may take up to 3 minutes to get a result.")
            if self.check_job_creation(upload_status['subid'],1):
                submission_status = astrometry.get_submission_status(upload_status['subid'])
                jobid = submission_status['jobs'][0]
                bot_msg.edit_text( text="Analyzing...")

                job_status = self.astrometry_check_job_status(jobid)
                if job_status is True:
                    final_image = astrometry.get_final_image(jobid)
                    
                    bot_msg.edit_text( text="Final image ready.")
                    try:    
                        try:
                            update.message.reply_photo(
                                photo= final_image,
                                reply_markup=InlineKeyboardMarkup(
                                    [
                                        [InlineKeyboardButton(text = "List identified objects", callback_data="list_astrometry_objects_{}".format(jobid))],
                                        [InlineKeyboardButton(text = "Detailed objects info", callback_data="detailed_astrometry_objects_{}".format(jobid))]
                                    ]
                                )
                            )
                        except:
                            update.message.reply_text(
                                text="Unable to fetch final image.",
                                reply_markup=InlineKeyboardMarkup(
                                    [
                                        [InlineKeyboardButton(text = "List identified objects", callback_data="list_astrometry_objects_{}".format(jobid))],
                                        [InlineKeyboardButton(text = "Detailed objects info", callback_data="detailed_astrometry_objects_{}".format(jobid))]
                                    ]
                                )
                            )
                    except Exception as e:
                        print(e)
                        try:
                            update.message.reply_photo(photo= final_image)
                        except:
                            update.message.reply_text(text = 'Unable to fetch final image.')
                    return -1
                else:
                    bot_msg.edit_text(text="Unable to solve the given image.")
                    if job_status is False:

                        try:
                            username = "@{}".format(update.message.from_user.username)
                        except:
                            username = update.message.from_user.first_name

                        data = {
                                'source': 'photobot',
                                'function': 'platesolve',
                                'astrometry_job_id': jobid,
                                'username': username,
                                'user_id': update.message.from_user.id,
                                'added_by': 'bot',
                                'added_on': datetime.datetime.now(tz=config.TIMEZONE)
                            }

                        admin_functions.update_watch_list(data, context)
                    return -1
            else:
                bot_msg.edit_text(text="Job took too long. Request closed.")
                return -1
        else:
            return -1

    @utils.is_not_blacklist
    @utils.is_approved
    def timeout(self, update: Update, context: CallbackContext):
        self.req_msg.edit_text(text="Your request timed out. Please try again.")
        return -1 

    @utils.is_not_blacklist
    @utils.is_approved
    def start_platesolve(self, update: Update, context: CallbackContext):
        try:
            self.login_data = astrometry.login()
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

    @utils.is_not_blacklist
    @utils.is_approved
    def cancel(self, update: Update, context: CallbackContext):
        context.bot.sendMessage(chat_id = update.message.chat_id, text="Cancelled request.")
        return -1

# ------------------------------------ GET INFO ON DEEPSKY OBJECTS -------------------------------------#

    @utils.is_not_blacklist
    @utils.is_approved
    def get_dso_data(self, update: Update, context: CallbackContext):
        
        search_text = update.message.text.split('/find')[1].strip()

        if search_text != '':
            
            if re.search('m[ ]*[0-9]+', search_text.lower()):
                search_text = re.sub('m[ ]*',"Messier ", search_text.lower())
            elif re.search('messier[0-9]+', search_text.lower()):
                search_text = re.sub('messier',"Messier ", search_text.lower())
            elif re.search('ngc[0-9]+', search_text.lower()):
                search_text = re.sub('ngc',"NGC ", search_text.lower())
            elif re.search('ic[0-9]+', search_text.lower()):
                search_text = re.sub('ic',"IC ", search_text.lower())
            elif re.search('(sharpless) *2-', search_text.lower()):
                search_text = re.sub('sharpless *2-', 'sh 2-', search_text.lower())
            elif re.search('(sh) *2-', search_text.lower()):
                search_text = re.sub('sh *2-', 'sh 2-', search_text.lower())
            elif re.search('(sharpless) *(?!2-)', search_text.lower()):
                search_text = re.sub('sharpless *', 'sh 2-', search_text.lower())
            elif re.search('(sh) *(?!2-)', search_text.lower()):
                search_text = re.sub('sh *', 'sh 2-', search_text.lower())
            elif re.search('^abell[ ]*[0-9]+', search_text.lower()):
                search_text = re.sub('^abell[ ]*','abell ', search_text.lower())
            print(search_text)
            search_object_index = search_text.replace(' ', '').lower()
            if search_object_index in config.DSO_DATA:
                found_object = config.DSO_DATA[search_object_index]

                if found_object['full_description'] is not None:

                    markup = InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton(text='Get detailed information', callback_data='full_dso_data_{}'.format(search_object_index))]
                        ]
                    )
                else:
                    markup = None

                update.message.reply_photo(
                    photo= found_object['image_link'],
                    caption= found_object['short_description'],
                    reply_markup= markup
                )
            else:
                update.message.reply_text(text="Object {} not found.".format(search_text))
        else:
            update.message.reply_text(text="Enter an object name to search.")
