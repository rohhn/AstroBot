from __future__ import absolute_import
from hac_bot.astrobot import AstroBot
from hac_bot.photobot import PhotoBot
from hac_bot.bookbot import BookBot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, CallbackQueryHandler, ConversationHandler
import re, os, sys
import logging

#main file
project_path = os.path.abspath(os.path.dirname(__file__))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.ERROR
)
logger = logging.getLogger(__name__)

def main():

    if os.environ['DEPLOYMENT_ENVIRONMENT'] == 'DEV':
        try:
            if sys.argv[1] == 'astrobot':
                AstroBot_Token = open('config/testbot.conf','r').read()
            elif sys.argv[1] == 'photobot':
                PhotoBot_Token = open('config/testbot.conf', 'r').read()
            elif sys.argv[1] == 'bookbot':
                BookBot_Token = open('config/testbot.conf','r').read()
        except:
            print("Enter which bot to test.")
            sys.exit(1)
        
    elif os.environ['DEPLOYMENT_ENVIRONMENT'] == 'PROD':
        AstroBot_Token = os.environ['ASTROBOT_TOKEN']
        PhotoBot_Token = os.environ['PHOTOBOT_TOKEN']
        BookBot_Token = os.environ['BOOKBOT_TOKEN']
    else:
        print("Development Environment not known. Check Environment variable - DEPLOYMENT_ENVIRONMENT")
        return

    AstroBot_Updater = Updater(AstroBot_Token, use_context= True, workers= 32)
    PhotoBot_Updater = Updater(PhotoBot_Token, use_context=True, workers= 32)
    BookBot_Updater = Updater(BookBot_Token, use_context=True, workers= 32)


    #------------------------- AstroBot functions -------------------------
    astrobot = AstroBot()
    astrobot_dispatcher = AstroBot_Updater.dispatcher
    astrobot_dispatcher.add_handler(CommandHandler('start',astrobot.help))
    astrobot_dispatcher.add_handler(CommandHandler('daily_articles',astrobot.send_daily_article, pass_job_queue = True))
    astrobot_dispatcher.add_handler(CommandHandler('stop_daily_articles',astrobot.stop_daily_article, pass_job_queue = True))
    astrobot_dispatcher.add_handler(CommandHandler('randomarticle',astrobot.send_random_article, run_async=True))
    astrobot_dispatcher.add_handler(CommandHandler('help',astrobot.help, run_async=True))
    astrobot_dispatcher.add_handler(CommandHandler('news', astrobot.send_news_article, pass_args=True, run_async= True))
    astrobot_dispatcher.add_handler(InlineQueryHandler(astrobot.send_inline_news, run_async= True))
    astrobot_dispatcher.add_handler(CommandHandler('wiki',astrobot.send_wiki_info, pass_args=True))
    astrobot_dispatcher.add_handler(CommandHandler('weather',astrobot.send_weather_data, pass_args=True, run_async= True))
    astrobot_dispatcher.add_handler(MessageHandler(Filters.location, astrobot.send_current_location_weather, run_async= True))
    astrobot_dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, astrobot.welcome_new_user, run_async=True))
    astrobot_dispatcher.add_handler(CommandHandler('book', astrobot.books_alert, pass_args=True))
    astrobot_dispatcher.add_handler(CommandHandler('rules', astrobot.hac_rules))
    astrobot_dispatcher.add_handler(CallbackQueryHandler(astrobot.callback_query_handler, pass_chat_data=True, pass_user_data= True))
    astrobot_dispatcher.add_handler(MessageHandler(Filters.regex(re.compile(r'who made you?', re.IGNORECASE)), astrobot.creator, run_async=True))
    AstroBot_Updater.start_polling()

    #------------------------- PhotoBot functions -------------------------
    photobot = PhotoBot()
    photobot_dispatcher = PhotoBot_Updater.dispatcher
    photobot_dispatcher.add_handler(CommandHandler('startapod', photobot.send_apod, pass_job_queue=True))
    photobot_dispatcher.add_handler(CommandHandler('stopapod', photobot.stop_apod, pass_job_queue=True))
    photobot_dispatcher.add_handler(CommandHandler('start',photobot.help))
    photobot_dispatcher.add_handler(CommandHandler('help',photobot.help))
    astrometry_handler  = ConversationHandler(entry_points = [CommandHandler('analyze',photobot.start_platesolve, run_async=True),CommandHandler('analyse',photobot.start_platesolve, run_async=True)],
                                    states = {
                                        1: [MessageHandler(Filters.photo | Filters.document, photobot.platesolve, run_async=True)], 
                                        -2: [MessageHandler(Filters.text | Filters.command, photobot.timeout, run_async=True)]
                                        },
                                    fallbacks =
                                        [CommandHandler('cancel', photobot.cancel, run_async=True)],
                                    conversation_timeout = 60,
                                    )
    photobot_dispatcher.add_handler(astrometry_handler)
    photobot_dispatcher.add_handler(CallbackQueryHandler(photobot.callback_query_handler, pass_chat_data=True))
    photobot_dispatcher.add_handler(MessageHandler(Filters.regex(re.compile(r'@HAC_PhotoBot tell me about', re.IGNORECASE)), photobot.get_dso_data, run_async=True))
    photobot_dispatcher.add_handler(MessageHandler(Filters.regex(re.compile(r'who made you?', re.IGNORECASE)), photobot.creator, run_async=True))
    PhotoBot_Updater.start_polling()

    #------------------------- BookBot functions -------------------------
    bookbot = BookBot()
    bookbot_dispatcher = BookBot_Updater.dispatcher
    bookbot_dispatcher.add_handler(InlineQueryHandler(bookbot.send_book, run_async= True))
    bookbot_dispatcher.add_handler(CommandHandler('book', bookbot.new_books, pass_args=True, run_async= True))
    bookbot_dispatcher.add_handler(CommandHandler('help', bookbot.help))
    bookbot_dispatcher.add_handler(CommandHandler('start', bookbot.help))
    BookBot_Updater.start_polling()

if __name__ == '__main__':
    main()
