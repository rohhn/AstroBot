import datetime
import re
import time

import requests
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackContext

from hac_bot import admin_functions
from pymongo.errors import ConfigurationError, ConnectionFailure, OperationFailure
from . import common_functions, astrometry, utils, config, backend


class PhotoBot:

    # ------------------------------------ APOD EVERYDAY -------------------------------------#

    async def get_apod(self, context):

        # API call
        url = f"https://api.nasa.gov/planetary/apod?api_key={config.APOD_KEY}"
        resp = requests.get(url).json()
        url = resp['url']
        date = "Date: " + str(resp['date'])
        title = "APOD - " + resp['title']
        explanation = resp['explanation']
        try:
            await context.bot.sendPhoto(chat_id=context.job.context, photo=url,
                                        caption=str(f"{title}\n\n{explanation}\n{date}"))
        except:
            message = f"<a href=\"{url}\"><b>{title}</b></a>\n\n\n{explanation}\n<i>{date}</i>\n"
            await context.bot.sendMessage(chat_id=context.job.context, text=message, parse_mode='HTML')

    async def start_apod(self, update: Update, context: CallbackContext):
        if all((utils.is_not_blacklist(update), utils.is_approved(update), utils.is_group_admin(update, context))):
            chat_id = update.message.chat_id

            try:  # add group details to DB
                if chat_id not in config.apod_active_groups:
                    if config.BACKEND == 1:
                        data = {
                            'group_id': chat_id,
                            'added_by': update.message.from_user.username,
                            'added_on': datetime.datetime.now(tz=config.TIMEZONE)
                        }
                        db_table_name = f"{config.MONGODB_DB_NAME}.apod_active_groups"  # Format: DB_NAME.TABLE_NAME

                        response = backend.find_one_in_table(data, db_table_name)

                        if response is None:
                            response = backend.insert_into_table(data, db_table_name)

                        config.apod_active_groups = backend.get_apod_active_groups(config.MONGODB_DB_NAME)
                    else:
                        config.apod_active_groups.append(chat_id)
                    status = 1
                else:
                    status = 0

            except (ConfigurationError, OperationFailure, ConnectionFailure) as error:
                error_msg = f"BACKEND ERROR!\n{error}"
                await update.message.reply_text(text=error_msg)
            else:
                if status == 1:
                    await update.message.reply_text(text=f"Added {chat_id} to approved groups.")
                else:
                    await update.message.reply_text(text=f"{chat_id} already added to approved groups.")

            job_removed = common_functions.remove_job(str(chat_id), context)
            if job_removed:
                r = await context.bot.sendMessage(chat_id=chat_id, text="Running instance terminated.")
                await context.bot.delete_message(chat_id, r.message_id)

            await context.bot.sendMessage(chat_id=chat_id, text="APOD started")
            await context.job_queue.run_daily(self.get_apod, time=config.APOD_TIME, context=chat_id, name=str(chat_id))

    async def stop_apod(self, update: Update, context: CallbackContext):
        if all((utils.is_not_blacklist(update), utils.is_approved(update), utils.is_group_admin(update, context))):
            job_removed = common_functions.remove_job(str(update.message.chat_id), context)
            if job_removed:
                await context.bot.sendMessage(chat_id=update.message.chat_id, text='APOD has been stopped.')

    # ------------------------------------ PLATESOLVE IMAGES -------------------------------------#

    def astrometry_check_job_status(self, jobid, count=1):
        if count < 11:
            time.sleep(15)
            job_status = astrometry.get_job_status(jobid)
            if job_status['status'] == 'success':
                return True
            elif job_status['status'] == 'failure':
                return False
            else:
                return self.astrometry_check_job_status(jobid, count + 1)
        return None

    def check_job_creation(self, subid, count=1):
        if count < 11:
            time.sleep(15)
            submission_status = astrometry.get_submission_status(subid)
            if len(submission_status['jobs']) > 0 and submission_status['jobs'][0] is not None:
                return True
            else:
                return self.check_job_creation(subid, count + 1)
        return False

    async def platesolve(self, update: Update, context: CallbackContext):
        if all((utils.is_not_blacklist(update), utils.is_approved(update))):
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
                    await context.bot.sendMessage(chat_id=update.message.chat_id, text='Only JPEG/PNG file types supported.')
                elif str(e) == 'Timed out':
                    await context.bot.sendMessage(chat_id=update.message.chat_id, text='File size too large. Limit 5MB')
                else:
                    await context.bot.sendMessage(chat_id=update.message.chat_id,
                                            text='Systems down. Please report the error to the admins.')
                return -1

            upload_status = astrometry.url_upload(image_url, self.login_data)
            if upload_status['status'] == 'success':
                bot_msg = await update.message.reply_text(
                    text="Uploaded successfully. It may take up to 3 minutes to get a result.")
                if self.check_job_creation(upload_status['subid'], 1):
                    submission_status = astrometry.get_submission_status(upload_status['subid'])
                    jobid = submission_status['jobs'][0]
                    await bot_msg.edit_text(text="Analyzing...")

                    job_status = self.astrometry_check_job_status(jobid)
                    if job_status is True:
                        final_image = astrometry.get_final_image(jobid)

                        await bot_msg.edit_text(text="Final image ready.")
                        try:
                            try:
                                await update.message.reply_photo(
                                    photo=final_image,
                                    reply_markup=InlineKeyboardMarkup(
                                        [
                                            [InlineKeyboardButton(text="List identified objects",
                                                                  callback_data="list_astrometry_objects_{}".format(
                                                                      jobid))],
                                            [InlineKeyboardButton(text="Detailed objects info",
                                                                  callback_data="detailed_astrometry_objects_{}".format(
                                                                      jobid))]
                                        ]
                                    )
                                )
                            except:
                                await update.message.reply_text(
                                    text="Unable to fetch final image.",
                                    reply_markup=InlineKeyboardMarkup(
                                        [
                                            [InlineKeyboardButton(text="List identified objects",
                                                                  callback_data="list_astrometry_objects_{}".format(
                                                                      jobid))],
                                            [InlineKeyboardButton(text="Detailed objects info",
                                                                  callback_data="detailed_astrometry_objects_{}".format(
                                                                      jobid))]
                                        ]
                                    )
                                )
                        except Exception as e:
                            print(e)
                            try:
                                await update.message.reply_photo(photo=final_image)
                            except:
                                await update.message.reply_text(text='Unable to fetch final image.')
                        return -1
                    else:
                        await bot_msg.edit_text(text="Unable to solve the given image.")
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

                            await admin_functions.update_watch_list(data, context)
                        return -1
                else:
                    await bot_msg.edit_text(text="Job took too long. Request closed.")
                    try:
                        username = "@{}".format(update.message.from_user.username)
                    except:
                        username = update.message.from_user.first_name

                    data = {
                        'source': 'photobot',
                        'function': 'platesolve',
                        'astrometry_job_id': None,  # jobid
                        'username': username,
                        'user_id': update.message.from_user.id,
                        'added_by': 'bot',
                        'added_on': datetime.datetime.now(tz=config.TIMEZONE)
                    }

                    await admin_functions.update_watch_list(data, context)
                    return -1
            else:
                return -1

    async def timeout(self, update: Update, context: CallbackContext):
        if all((utils.is_not_blacklist(update), utils.is_approved(update))):
            await self.req_msg.edit_text(text="Your request timed out. Please try again.")
            return -1

    async def start_platesolve(self, update: Update, context: CallbackContext):
        if all((utils.is_not_blacklist(update), utils.is_approved(update))):
            try:
                self.login_data = astrometry.login()
                if self.login_data['status'] == 'success':
                    self.req_msg = await update.message.reply_text(
                        text='Send me a picture to analyze.\n\nType /cancel to abort the request.')
                    return 1
                else:
                    await context.bot.sendMessage(chat_id=update.message.chat_id,
                                            text='Systems down. Please report the error to the admins.')
                    return -1
            except ConnectionError:
                self.req_msg = await update.message.reply_text(text='Connection error. Please try again.')
                return -1
            except:
                self.req_msg = await update.message.reply_text(text='Systems down. Please report the error to the admins.')
                return -1

    async def cancel(self, update: Update, context: CallbackContext):
        if all((utils.is_not_blacklist(update), utils.is_approved(update))):
            await context.bot.sendMessage(chat_id=update.message.chat_id, text="Cancelled request.")
            return -1

    # ------------------------------------ GET INFO ON DEEPSKY OBJECTS -------------------------------------#

    async def get_dso_data(self, update: Update, context: CallbackContext):
        if all((utils.is_not_blacklist(update), utils.is_approved(update))):
            search_text = update.message.text.split('/find')[1].strip()

            if search_text != '':

                if re.search('m[ ]*[0-9]+', search_text.lower()):
                    search_text = re.sub('m[ ]*', "Messier ", search_text.lower())
                elif re.search('messier[0-9]+', search_text.lower()):
                    search_text = re.sub('messier', "Messier ", search_text.lower())
                elif re.search('ngc[0-9]+', search_text.lower()):
                    search_text = re.sub('ngc', "NGC ", search_text.lower())
                elif re.search('ic[0-9]+', search_text.lower()):
                    search_text = re.sub('ic', "IC ", search_text.lower())
                elif re.search('(sharpless) *2-', search_text.lower()):
                    search_text = re.sub('sharpless *2-', 'sh 2-', search_text.lower())
                elif re.search('(sh) *2-', search_text.lower()):
                    search_text = re.sub('sh *2-', 'sh 2-', search_text.lower())
                elif re.search('(sharpless) *(?!2-)', search_text.lower()):
                    search_text = re.sub('sharpless *', 'sh 2-', search_text.lower())
                elif re.search('(sh) *(?!2-)', search_text.lower()):
                    search_text = re.sub('sh *', 'sh 2-', search_text.lower())
                elif re.search('^abell[ ]*[0-9]+', search_text.lower()):
                    search_text = re.sub('^abell[ ]*', 'abell ', search_text.lower())
                print(search_text)
                search_object_index = search_text.replace(' ', '').lower()
                if search_object_index in config.DSO_DATA:
                    found_object = config.DSO_DATA[search_object_index]

                    if found_object['full_description'] is not None:

                        markup = InlineKeyboardMarkup(
                            [
                                [InlineKeyboardButton(text='Get detailed information',
                                                      callback_data='full_dso_data_{}'.format(search_object_index))]
                            ]
                        )
                    else:
                        markup = None

                    await update.message.reply_photo(
                        photo=found_object['image_link'],
                        caption=found_object['short_description'],
                        reply_markup=markup
                    )
                else:
                    await update.message.reply_text(text="Object {} not found.".format(search_text))
            else:
                await update.message.reply_text(text="Enter an object name to search.")
