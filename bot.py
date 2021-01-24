from __future__ import absolute_import
from hac_bot.astrobot import AstroBot
from hac_bot.photobot import PhotoBot
from hac_bot.bookbot import BookBot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, CallbackQueryHandler, ConversationHandler

#main file

def main():
    AstroBot_Token = open('config/astrobot.conf','r').read()
    PhotoBot_Token = open('config/testbot.conf', 'r').read()
    BookBot_Token = open('config/bookbot.conf','r').read()

    AstroBot_Updater = Updater(AstroBot_Token, use_context= True, workers= 32)
    PhotoBot_Updater = Updater(PhotoBot_Token, use_context=True, workers= 32)
    BookBot_Updater = Updater(BookBot_Token, use_context=True, workers= 32)

    #astrobot = AstroBot()
    #astrobot_dispatcher = AstroBot_Updater.dispatcher
    #astrobot_dispatcher.add_handler(CommandHandler('start',astrobot.help))
    #astrobot_dispatcher.add_handler(CommandHandler('daily_articles',astrobot.get_article, pass_job_queue = True))
    #astrobot_dispatcher.add_handler(CommandHandler('stop_daily_articles',astrobot.stop_func, pass_job_queue = True))
    #astrobot_dispatcher.add_handler(CommandHandler('randomarticle',astrobot.random_article))
    #astrobot_dispatcher.add_handler(CommandHandler('help',astrobot.help))
    #astrobot_dispatcher.add_handler(CommandHandler('news', astrobot.fetch_article, pass_args=True, run_async= True))
    #astrobot_dispatcher.add_handler(InlineQueryHandler(astrobot.news_articles_inline, run_async= True))
    #astrobot_dispatcher.add_handler(CommandHandler('wiki',astrobot.get_wiki_info, pass_args=True))
    #astrobot_dispatcher.add_handler(CommandHandler('weather',astrobot.get_weather, pass_args=True, run_async= True))
    #astrobot_dispatcher.add_handler(MessageHandler(Filters.location, astrobot.current_location_weather, run_async= True))
    #astrobot_dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, astrobot.welcome_new_user))
    #astrobot_dispatcher.add_handler(CommandHandler('book', astrobot.books_alert, pass_args=True))
    #astrobot_dispatcher.add_handler(CallbackQueryHandler(astrobot.callback_query_handler, pass_chat_data=True, pass_user_data= True))
    #AstroBot_Updater.start_polling()

    photobot = PhotoBot()
    photobot_dispatcher = PhotoBot_Updater.dispatcher
    photobot_dispatcher.add_handler(CommandHandler('startapod', photobot.daily_job, pass_job_queue=True))
    photobot_dispatcher.add_handler(CommandHandler('stopapod', photobot.stop_func, pass_job_queue=True))
    photobot_dispatcher.add_handler(CommandHandler('start',photobot.help))
    photobot_dispatcher.add_handler(CommandHandler('help',photobot.help))
    astrometry_handler  = ConversationHandler(entry_points = [CommandHandler('analyze',photobot.start_platesolve, run_async=True),CommandHandler('analyse',photobot.start_platesolve, run_async=True)],
                                    states = {
                                        1: [MessageHandler(Filters.photo, photobot.platesolve, run_async=True)], 
                                        -2: [MessageHandler(Filters.text | Filters.command, photobot.timeout, run_async=True)]
                                        },
                                    fallbacks =
                                        [CommandHandler('cancel', photobot.cancel, run_async=True)],
                                    conversation_timeout = 60,
                                    )
    photobot_dispatcher.add_handler(astrometry_handler)
    photobot_dispatcher.add_handler(CallbackQueryHandler(photobot.callback_query_handler, pass_chat_data=True))
    PhotoBot_Updater.start_polling()

    #bookbot = BookBot()
    #bookbot_dispatcher = BookBot_Updater.dispatcher
    #bookbot_dispatcher.add_handler(InlineQueryHandler(bookbot.send_book, run_async= True))
    #bookbot_dispatcher.add_handler(CommandHandler('book', bookbot.new_books, pass_args=True, run_async= True))
    #bookbot_dispatcher.add_handler(CommandHandler('help', bookbot.help))
    #bookbot_dispatcher.add_handler(CommandHandler('start', bookbot.help))
    #BookBot_Updater.start_polling()

if __name__ == '__main__':
    main()