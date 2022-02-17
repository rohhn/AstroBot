import telegram
from telegram import Update
from telegram.ext import CallbackContext
from . import utils, config


@utils.is_bot_admin
def add_group(update: Update, context: CallbackContext):
    
    new_chat_id = update.message.text.split('/add_group')[1].strip()
    if new_chat_id:
        if new_chat_id not in config.approved:
            config.approved.append(new_chat_id)
            update.message.reply_text(text=f"Added {new_chat_id} to approved groups.")
        else:
            update.message.reply_text(text=f"{new_chat_id} already added to approved groups.")


@utils.is_bot_admin
def remove_group(update: Update, context: CallbackContext):
    
    new_chat_id = update.message.text.split('/remove_group')[1].strip()
    if new_chat_id:
        try:
            config.approved.remove(new_chat_id)
            update.message.reply_text(text=f"Removed {new_chat_id} from approved groups.")
        except ValueError:
            update.message.reply_text(text=f"{new_chat_id} not in approved groups.")


@utils.is_bot_admin
def admin_helper(update: Update, context: CallbackContext):

    msg = "/add_group <chat_id>: Add a new group to list of authorized groups\n\n/remove_group <chat_id>: Remove a group from list of authorized groups"

    update.message.reply_text(text=msg)
