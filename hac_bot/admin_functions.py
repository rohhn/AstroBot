import telegram
from . import utils, config


@utils.is_bot_admin
def add_group(update: telegram.Update, context):
    
    new_chat_id = update.message.text.split('/add_group')[1].strip()
    if new_chat_id:
        if new_chat_id not in config.approved:
            config.approved.append(new_chat_id)
            update.message.reply_text(text=f"Added {new_chat_id} to approved groups.")
        else:
            update.message.reply_text(text=f"{new_chat_id} already added to approved groups.")

@utils.is_bot_admin
def remove_group(update: telegram.Update, context):
    
    new_chat_id = update.message.text.split('/remove_group')[1].strip()
    if new_chat_id:
        try:
            config.approved.remove(new_chat_id)
            update.message.reply_text(text=f"Removed {new_chat_id} from approved groups.")
        except ValueError:
            update.message.reply_text(text=f"{new_chat_id} not in approved groups.")
