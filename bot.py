import os
import sys
import logging
from hac_bot import common_functions, admin_functions
from hac_bot.astrobot import AstroBot
from hac_bot.photobot import PhotoBot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, CallbackQueryHandler, ConversationHandler

#main file
project_path = os.path.abspath(os.path.dirname(__file__))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.ERROR
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":

    try:
        token = os.environ['BOT_TOKEN']
    except KeyError:
        print("Save bot token in environment as 'BOT_TOKEN'.")
        sys.exit(1)

    bot_updater = Updater(token, use_context= True, workers= 32)

    #------------------------- AstroBot functions -------------------------
    astrobot = AstroBot()
    photobot = PhotoBot()
    # bookbot = BookBot()

    bot_dispatcher = bot_updater.dispatcher

    bot_dispatcher.add_handler(CommandHandler('start',common_functions.bot_help))
    bot_dispatcher.add_handler(CommandHandler('help',common_functions.bot_help, run_async=True))

    bot_dispatcher.add_handler(CommandHandler('daily_articles',astrobot.send_daily_article, pass_job_queue = True))
    bot_dispatcher.add_handler(CommandHandler('stop_daily_articles',astrobot.stop_daily_article, pass_job_queue = True))
    bot_dispatcher.add_handler(CommandHandler('randomarticle',astrobot.send_random_article, run_async=True))
    bot_dispatcher.add_handler(CommandHandler('news', astrobot.send_news_article, pass_args=True, run_async= True))
    bot_dispatcher.add_handler(InlineQueryHandler(astrobot.send_inline_news, run_async= True))
    bot_dispatcher.add_handler(CommandHandler('wiki',astrobot.send_wiki_info, pass_args=True))
    bot_dispatcher.add_handler(CommandHandler('weather',astrobot.send_weather_data, pass_args=True, run_async= True))
    bot_dispatcher.add_handler(MessageHandler(Filters.location, astrobot.send_current_location_weather, run_async= True))
    bot_dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, astrobot.welcome_new_user, run_async=True))
    # bot_dispatcher.add_handler(CommandHandler('rules', astrobot.hac_rules))
    bot_dispatcher.add_handler(CommandHandler('credits', common_functions.bot_credits, run_async=True))

    #------------------------- PhotoBot functions -------------------------
    
    bot_dispatcher.add_handler(CommandHandler('startapod', photobot.send_apod, pass_job_queue=True))
    bot_dispatcher.add_handler(CommandHandler('stopapod', photobot.stop_apod, pass_job_queue=True))
    astrometry_handler  = ConversationHandler(
        entry_points=[
            CommandHandler('analyze',photobot.start_platesolve, run_async=True),
            CommandHandler('analyse',photobot.start_platesolve, run_async=True)
        ],
        states={
            1: [MessageHandler(Filters.photo | Filters.document, photobot.platesolve, run_async=True)], 
            -2: [MessageHandler(Filters.text | Filters.command, photobot.timeout, run_async=True)]
        },
        fallbacks=[
            CommandHandler('cancel', photobot.cancel, run_async=True)
        ],
        conversation_timeout = 60,
    )
    bot_dispatcher.add_handler(astrometry_handler)
    bot_dispatcher.add_handler(CommandHandler('find', photobot.get_dso_data, run_async=True))

    # #------------------------- BookBot functions -------------------------
    
    # bot_dispatcher.add_handler(InlineQueryHandler(bookbot.send_book, run_async= True))
    # bot_dispatcher.add_handler(CommandHandler('book', bookbot.new_books, pass_args=True, run_async= True))

    #------------------------- Admin functions -------------------------
    bot_dispatcher.add_handler(CommandHandler('add_group', admin_functions.add_group, pass_args=True, run_async=True))
    bot_dispatcher.add_handler(CommandHandler('remove_group', admin_functions.remove_group, pass_args=True, run_async=True))

    bot_dispatcher.add_handler(CallbackQueryHandler(common_functions.callback_query_handler, pass_chat_data=True, pass_user_data= True))

    bot_updater.start_polling()
