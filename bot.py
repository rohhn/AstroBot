from __future__ import absolute_import
from hac_bot.astrobot import AstroBot
from hac_bot.photobot import PhotoBot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, CallbackQueryHandler, ConversationHandler


def main():
    AstroBot_Token = open('config/astrobot.conf','r').read()
    PhotoBot_Token = open('config/photobot.conf', 'r').read()
    BookBot_Token = open('config/bookbot.conf','r').read()


    AstroBot_Updater = Updater(AstroBot_Token, use_context= True)
    PhotoBot_Updater = Updater(PhotoBot_Token, use_context=True)
    BookBot_Updater = Updater(BookBot_Token, use_context=True)

    astrobot = AstroBot()
    

    
    astrobot_dispatcher = AstroBot_Updater.dispatcher
    astrobot_dispatcher.add_handler(CommandHandler('start',astrobot.bot_help))
    astrobot_dispatcher.add_handler(CommandHandler('daily_articles',astrobot.get_article, pass_job_queue = True))
    astrobot_dispatcher.add_handler(CommandHandler('stop_daily_articles',astrobot.stop_func, pass_job_queue = True))
    astrobot_dispatcher.add_handler(CommandHandler('randomarticle',astrobot.random_article))
    astrobot_dispatcher.add_handler(CommandHandler('help',astrobot.help))
    astrobot_dispatcher.add_handler(CommandHandler('news', astrobot.fetch_article, pass_args=True))
    astrobot_dispatcher.add_handler(InlineQueryHandler(astrobot.news_articles_inline))
    astrobot_dispatcher.add_handler(CommandHandler('wiki',astrobot.get_wiki_info, pass_args=True))
    astrobot_dispatcher.add_handler(CommandHandler('weather',astrobot.get_weather, pass_args=True))
    astrobot_dispatcher.add_handler(MessageHandler(Filters.location, astrobot.current_location_weather))
    astrobot_dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, astrobot.welcome_new_user))
    astrobot_dispatcher.add_handler(CommandHandler('book', astrobot.books_alert, pass_args=True))
    astrobot_dispatcher.add_handler(CallbackQueryHandler(astrobot.callback_query_handler, pass_chat_data=True))
    AstroBot_Updater.start_polling()

    photobot = PhotoBot()
    photobot_dispatcher = PhotoBot_Updater.dispatcher
    photobot_dispatcher.add_handler(CommandHandler('startapod', photobot.daily_job, pass_job_queue=True))
    photobot_dispatcher.add_handler(CommandHandler('stopapod', photobot.stop_func, pass_job_queue=True))
    photobot_dispatcher.add_handler(CommandHandler('help',photobot.help))
    astrometry_handler  = ConversationHandler(entry_points = [CommandHandler('analyze',photobot.start_platesolve)],
                                    states = {
                                        1: [MessageHandler(Filters.photo, photobot.platesolve)]},
                                    fallbacks =
                                        [CommandHandler('cancel', photobot.cancel)]
                                    )
    photobot_dispatcher.add_handler(astrometry_handler)
    PhotoBot_Updater.start_polling()

    bookbot_dispatcher = BookBot_Updater.dispatcher
    bookbot_dispatcher.add_handler(InlineQueryHandler(astrobot.send_book))
    bookbot_dispatcher.add_handler(CommandHandler('book', astrobot.new_books, pass_args=True))
    BookBot_Updater.start_polling()

if __name__ == '__main__':
    main()