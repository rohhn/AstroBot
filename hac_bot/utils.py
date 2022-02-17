from telegram import Update
from telegram.ext import CallbackContext
from . import config


def is_approved(func):

    def check(*args, **kwargs):
        for arg in args:
            if isinstance(arg, Update):
                update = arg

        if update.message.chat.type != 'private':
            if str(update.message.chat.id) not in config.approved_groups:
                return False
        func(*args, **kwargs)
        return True

    return check


def is_bot_admin(func):

    def check(*args, **kwargs):
        for arg in args:
            if isinstance(arg, Update):
                update = arg

        if str(update.message.from_user.id) not in config.BOT_ADMINS:
            return False
        func(*args, **kwargs)    
        return True

    return check


def is_group_admin(func):

    def check(*args, **kwargs):
        for arg in args:
            if isinstance(arg, Update):
                update = arg
            if isinstance(arg, CallbackContext):
                context = arg

        if update.message.chat.type != 'private':
            admins = [admin.user.id for admin in context.bot.get_chat_administrators(update.message.chat.id)]
            if update.message.from_user.id not in admins:
                return False
        func(*args, **kwargs)
        return True

    return check


def is_not_blacklist(func):

    def check(*args, **kwargs):
        for arg in args:
            if isinstance(arg, Update):
                update = arg

        if str(update.message.from_user.id) in config.blacklist:
            return False
        func(*args, **kwargs)    
        return True

    return check