from telegram import Update
from telegram.ext import CallbackContext

from . import config


def is_approved(update: Update):

    if update.message.chat.type == 'private' or str(update.message.chat.id) in config.apod_active_groups:
        return True

    return False


def is_apod_active(update: Update):

    if update.message.chat.type == 'private' or str(update.message.chat.id) in config.apod_active_groups:
        return True

    return False


def is_bot_admin(update: Update):

    if str(update.message.from_user.id) in config.BOT_ADMINS:
        return True

    return False


def is_group_admin(update: Update, context):

    if update.message.chat.type != 'private':
        admins = [admin.user.id for admin in context.bot.get_chat_administrators(update.message.chat.id)]
        if update.message.from_user.id in admins:
            return True

    return False


def is_not_blacklist(update: Update):

    if str(update.message.from_user.id) not in config.blacklist:
        return True

    return False
