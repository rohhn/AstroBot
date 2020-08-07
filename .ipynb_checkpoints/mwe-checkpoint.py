import datetime
import pytz
from telegram.ext import Updater, CommandHandler, JobQueue

indt = pytz.timezone("Asia/Kolkata")
    
def sendamessage(bot,job):
    bot.sendMessage(chat_id=job.context.message.chat_id, text="test message")
    

def daily_job(bot, update, job_queue):
    bot.sendMessage(chat_id=update.message.chat_id, text="started")
    job_queue.run_daily(sendamessage, time= datetime.time(23,40,0,0, tzinfo=indt), context=update)

def stop_bot(bot, update, job_queue):
    bot.sendMessage(chat_id=update.message.chat_id,
                      text='stopped')
    job_queue.stop()

updater = Updater("1183471904:AAGpCR_ox0jDU21ii3Lv00moJmrFp8fCMmg")
dp = updater.dispatcher
dp.add_handler(CommandHandler('start', daily_job, pass_job_queue=True))
dp.add_handler(CommandHandler('stop', stop_bot, pass_job_queue=True))

updater.start_polling()
    
    
    