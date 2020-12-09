from AstroBot import AstroBot
from PhotoBot import PhotoBot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


def main():
    AstroBot_Token = open('config/astrobot.conf','r').read()
    PhotoBot_Token = open('config/photobot.conf', 'r').read()

    AstroBot_Updater = Updater(AstroBot_Token, use_context= True)
    PhotoBot_Updater = Updater(PhotoBot_Token, use_context=True)


    astrobot = AstroBot()
    astrobot_dispatcher = AstroBot_Updater.dispatcher
    astrobot_dispatcher.add_handler(CommandHandler('weekly_articles',astrobot.get_article, pass_job_queue = True))
    astrobot_dispatcher.add_handler(CommandHandler('stop_weekly_articles',astrobot.stop_func, pass_job_queue = True))
    astrobot_dispatcher.add_handler(CommandHandler('randomarticle',astrobot.random_article))
    astrobot_dispatcher.add_handler(CommandHandler('help',astrobot.bot_help))
    astrobot_dispatcher.add_handler(CommandHandler('news', astrobot.fetch_article, pass_args=True))
    astrobot_dispatcher.add_handler(CommandHandler('wiki',astrobot.get_wiki_info, pass_args=True))
    astrobot_dispatcher.add_handler(CommandHandler('weather',astrobot.get_weather, pass_args=True))
    astrobot_dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, astrobot.welcome_new_user))
    AstroBot_Updater.start_polling()

    photobot = PhotoBot()
    photobot_dispatcher = PhotoBot_Updater.dispatcher
    photobot_dispatcher.add_handler(CommandHandler('startapod', photobot.daily_job, pass_job_queue=True))
    photobot_dispatcher.add_handler(CommandHandler('stopapod', photobot.stop_func, pass_job_queue=True))
    PhotoBot_Updater.start_polling()


if __name__ == '__main__':
    main()