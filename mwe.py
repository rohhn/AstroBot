import datetime
import pytz
from telegram.ext import Updater, CommandHandler, JobQueue

indt = pytz.timezone("Asia/Kolkata")
    
def sendamessage(bot,job):
    bot.sendMessage(chat_id=job.context.message.chat_id, text="system: "+str(datetime.datetime.now()) + "\nIndia: \n"+str(datetime.datetime.now().astimezone(indt).strftime("%H"))+" - "+str(datetime.datetime.now().astimezone(indt).strftime("%M"))+" - "+str(datetime.datetime.now().astimezone(indt).strftime("%S"))+datetime.datetime.time(22,15,0,0, tzinfo=indt))
    

def daily_job(bot, update, job_queue):
    bot.sendMessage(chat_id=update.message.chat_id, text=("started"))
    job_queue.run_repeating(sendamessage,60, context=update) #time= datetime.time(13,00,0,0, tzinfo=indt), context=update)

def stop_bot(bot, update, job_queue):
    bot.sendMessage(chat_id=update.message.chat_id,
                      text='stopped')
    job_queue.stop()

updater = Updater("1183471904:AAHzW9eC9XIHJwJXRiyRKrJemA3WVxY_mug")
dp = updater.dispatcher
dp.add_handler(CommandHandler('start', daily_job, pass_job_queue=True))
dp.add_handler(CommandHandler('stop', stop_bot, pass_job_queue=True))

updater.start_polling()
    
    
    