from telegram.ext import Updater, CommandHandler, JobQueue, Filters
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import os
#from hac_bot.astrobot import Helper

PORT = int(os.environ.get('PORT',8443))

def file_func(update, context):
    if update.message.photo:
        file = update.message.photo[-1].get_file()
    else:
        file = update.message.document.get_file()
    print(file)
    #print(update)
    print('-'*25)
    try:
        if update.message.document.mime_type == 'image/jpeg' or update.message.document.mime_type == 'image/png':
            print(update.message.document.get_file()['file_path'])
        else:
            raise Exception('non-image')
    except Exception as e:
        if e.args == 'non-image':
            print('not an image')
        else:
            print(e)

def photo_func(update, context):
    print(update.message.photo[-1])

def test(update, context):
    update.message.reply_text('heard')

def main():
    TOKEN = "1183471904:AAFTQWt9L9_q79sDzhU7WCtWK573bl7eCiU"
    AstroBot_Updater = Updater(TOKEN, use_context= True, workers=32)
    astrobot_dispatcher = AstroBot_Updater.dispatcher
    astrobot_dispatcher.add_handler(CommandHandler('yo',test))
    #astrobot_dispatcher.add_handler(MessageHandler(Filters.all, test))
    #astrobot_dispatcher.add_handler(MessageHandler((Filters.regex(re.compile(r'tell me about', re.IGNORECASE))) | (Filters.regex(re.compile(r'tell me about', re.IGNORECASE)) & Filters.entity('mention')), test))
    #astrobot_dispatcher.add_handler(MessageHandler(Filters.photo, photo_func))
    #AstroBot_Updater.start_polling()
    AstroBot_Updater.start_webhook(listen='0.0.0.0',
                                    port=int(PORT),
                                    url_path=TOKEN)
    
    AstroBot_Updater.bot.setWebhook('https://hac-bot.herokuapp.com/'+TOKEN)
    AstroBot_Updater.idle()


if __name__ == '__main__':
    main()