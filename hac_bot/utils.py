from telegram import Update
from . import config


def is_approved(func):

    def check(*args, **kwargs):
        for arg in args:
            if isinstance(arg, Update):
                update = arg

        if update.message.chat.type != 'private':
            if str(update.message.chat.id) not in config.approved:
                return False
        func(*args, **kwargs)
        return True

    return check


def is_bot_admin(func):

    def check(*args, **kwargs):
        for arg in args:
            if isinstance(arg, Update):
                update = arg

        if str(update.message.from_user.id) not in config.bot_admins:
            return False
        func(*args, **kwargs)    
        return True

    return check
