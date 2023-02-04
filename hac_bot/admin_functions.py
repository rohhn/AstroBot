import datetime
from pymongo.errors import ConfigurationError, ConnectionFailure, OperationFailure
from telegram import Update
from telegram.ext import CallbackContext

from . import utils, config, backend


async def add_group(update: Update, context: CallbackContext):
    if utils.is_bot_admin(update):
        new_chat_id = update.message.text.split('/add_group')[1].strip()

        if new_chat_id:
            try:
                if new_chat_id not in config.apod_active_groups:
                    if config.BACKEND == 1:
                        data = {
                            'group_id': new_chat_id,
                            'added_by': update.message.from_user.username,
                            'added_on': datetime.datetime.now(tz=config.TIMEZONE)
                        }
                        db_table_name = f"{config.MONGODB_DB_NAME}.approved_groups"  # Format: DB_NAME.TABLE_NAME

                        response = backend.find_one_in_table(data, db_table_name)

                        if response is None:
                            response = backend.insert_into_table(data, db_table_name)

                        config.apod_active_groups = backend.get_approved_groups(config.MONGODB_DB_NAME)
                    else:
                        config.apod_active_groups.append(new_chat_id)
                    status = 1
                else:
                    status = 0

            except (ConfigurationError, OperationFailure, ConnectionFailure) as error:
                error_msg = f"BACKEND ERROR!\n{error}"
                await update.message.reply_text(text=error_msg)
            else:
                if status == 1:
                    await update.message.reply_text(text=f"Added {new_chat_id} to approved groups.")
                else:
                    await update.message.reply_text(text=f"{new_chat_id} already added to approved groups.")


async def remove_group(update: Update, context: CallbackContext):
    if utils.is_bot_admin(update):
        new_chat_id = update.message.text.split('/remove_group')[1].strip()
        if new_chat_id:
            try:
                if config.BACKEND == 1:
                    data = {'group_id': new_chat_id}
                    db_table_name = f"{config.MONGODB_DB_NAME}.approved_groups"

                    response = backend.delete_one_from_table(data, db_table_name)

                    config.apod_active_groups = backend.get_approved_groups(config.MONGODB_DB_NAME)
                else:
                    config.apod_active_groups.remove(new_chat_id)

            except ValueError:
                await update.message.reply_text(text=f"{new_chat_id} not in approved groups.")
            except (ConfigurationError, OperationFailure, ConnectionFailure) as error:
                error_msg = f"BACKEND ERROR!\n{error}"
                await update.message.reply_text(text=error_msg)
            else:
                await update.message.reply_text(text=f"Removed {new_chat_id} from approved groups.")


async def admin_helper(update: Update, context: CallbackContext):

    msg = """/add_group <chat_id>: Add a new group to list of authorized groups\n
/remove_group <chat_id>: Remove a group from list of authorized groups\n
/blacklist <chat_id>: Ban a user from using the bot.\n
/whitelist <chat_id>: Unban a user from using the bot.\n
/warn <chat_id>: Add a user to the ban watchlist. 3 warnings will lead to a ban. (Only supported with MongoDB backend)"""
    if utils.is_bot_admin(update):
        await update.message.reply_text(text=msg)


async def update_watch_list(data, context: CallbackContext):
    if config.BACKEND == 1:

        db_table_name = f"{config.MONGODB_DB_NAME}.blacklist_users"

        try:

            backend.update_watchlist_table(data, db_table_name)

            config.blacklist = backend.get_blacklist_users(db=config.MONGODB_DB_NAME)

        except Exception as common_exception:
            print(f"ERROR UPDATING BLACKLIST: {common_exception}")

    if config.ADMIN_CHAT:
        failure_info = "Username: {}\nUser ID: {}\nFunction: {}".format(data['username'], data['user_id'],
                                                                        data['function'])

        if data['function'] == 'platesolve':
            failure_info += "\nJob ID: {}".format(data['astrometry_job_id'])

        await context.bot.sendMessage(
            chat_id=config.ADMIN_CHAT,
            text=failure_info
        )


async def add_user_to_blacklist(update: Update, context: CallbackContext):
    if utils.is_bot_admin(update):
        new_chat_id = update.message.text.split('/blacklist')[1].strip()

        if new_chat_id in config.BOT_ADMINS:
            await update.message.reply_text("Et tu, Brute?")
            return

        data = {
            'user_id': new_chat_id,
            'added_by': update.message.from_user.username,
            'infringement_count': 3,
            'added_on': datetime.datetime.now(tz=config.TIMEZONE)
        }

        if new_chat_id not in config.blacklist:

            if config.BACKEND == 1:
                db_table_name = f"{config.MONGODB_DB_NAME}.blacklist_users"

                backend.update_watchlist_table(data, db_table_name)
                config.blacklist = backend.get_blacklist_users(db=config.MONGODB_DB_NAME)
            else:
                config.blacklist.append(new_chat_id)

            await update.message.reply_text(f"Added {new_chat_id} to blacklist.")
        else:
            await update.message.reply_text(f"{new_chat_id} already in blacklist.")


async def remove_user_from_blacklist(update: Update, context: CallbackContext):
    if utils.is_bot_admin(update):
        new_chat_id = update.message.text.split('/whitelist')[1].strip()

        data = {
            'user_id': new_chat_id,
            'added_by': update.message.from_user.username,
            'infringement_count': 0
        }

        if new_chat_id in config.blacklist:

            if config.BACKEND == 1:

                db_table_name = f"{config.MONGODB_DB_NAME}.blacklist_users"
                backend.update_watchlist_table(data, db_table_name)
                config.blacklist = backend.get_blacklist_users(db=config.MONGODB_DB_NAME)
            else:
                config.blacklist.remove(new_chat_id)
            await update.message.reply_text(f"Removed {new_chat_id} from blacklist.")
        else:
            await update.message.reply_text(f"{new_chat_id} not in blacklist.")


async def warn_user(update: Update, context: CallbackContext):
    if utils.is_bot_admin(update):
        new_chat_id = update.message.text.split('/warn')[1].strip()

        if new_chat_id in config.BOT_ADMINS:
            await update.message.reply_text("Et tu, Brute?")
            return

        data = {
            'user_id': new_chat_id,
            'added_by': update.message.from_user.username,
            'added_on': datetime.datetime.now(tz=config.TIMEZONE)
        }

        if new_chat_id not in config.blacklist:

            if config.BACKEND == 1:
                db_table_name = f"{config.MONGODB_DB_NAME}.blacklist_users"

                backend.update_watchlist_table(data, db_table_name)
                config.blacklist = backend.get_blacklist_users(db=config.MONGODB_DB_NAME)
            # else:
            #     config.blacklist.append(new_chat_id)

            await update.message.reply_text(f"Added {new_chat_id} to watchlist.")
        else:
            await update.message.reply_text(f"{new_chat_id} already in blacklist.")
