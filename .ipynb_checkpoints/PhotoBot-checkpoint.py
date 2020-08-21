from bs4 import BeautifulSoup as bs4
import requests
from telegram import Bot
import datetime
import pytz
import hashlib
import re
from telegram.ext import Updater, CommandHandler, JobQueue

token = "1163369796:AAGmNm8peqmRL7Bf9LPwg5RYsqDfs9LHbrQ"

indt = pytz.timezone("Asia/Kolkata")

def get_url(page_text):
    if(page_text.find('img')):
        url = "https://apod.nasa.gov/apod/"+page_text.find_all('center')[0].find('img')['src']
        return(url)
    elif(page_text.find('iframe')):
        url = page_text.find_all('center')[0].find('iframe')['src']
        return url
    
def get_title(page_text):
    if(page_text.find('img')):
        return(re.sub("  +","",page_text.find_all('center')[1].get_text().replace("\n"," ").split("Image")[0]))
    elif(page_text.find('iframe')):
        return(re.sub("  +","",page_text.find_all('center')[1].get_text().replace("\n"," ").split("Video")[0]))
    
def sendmessage(context):
    url = "https://apod.nasa.gov/apod/astropix.html"
    response = requests.get(url)
    page_text = bs4(response.text,'html.parser')
    date = page_text.find("p").contents[3].get_text().replace('\n','')
    url = get_url(page_text)
    title = get_title(page_text)
    explanation = re.sub("  +","",page_text.find_all('p')[2].get_text().replace("\n"," ").split("Tomorrow")[0].split("Explanation: ")[1])
    if(page_text.find('img')):
        try:
            context.bot.sendPhoto(chat_id=context.job.context, photo=url, caption = str("APOD - "+title+"\n\n"+explanation+"\nDate: " + date))
        except:
            message = ("<a href=\""+url+"\">" +"<b>APOD - " + title + "</b></a>\n\n" +"\n" +explanation+"\n<i>Date: "+date+"</i>\n")
            context.bot.sendMessage(chat_id=context.job.context, text=message, parse_mode='HTML')
    elif(page_text.find('iframe')):
        message = ("<a href=\""+url+"\">" +"<b>APOD - " + title + "</b></a>\n\n" +"\n" +explanation+"\n<i>Date: "+date+"</i>\n")
        context.bot.sendMessage(chat_id=context.job.context, text=message, parse_mode='HTML')
    return()
    

def daily_job(update, context):
    context.bot.sendMessage(chat_id=update.message.chat_id, text="started")
    context.job_queue.run_daily(sendmessage,time=datetime.time(11,23,0,tzinfo=indt), context=update.message.chat_id)
    #job_queue.run_repeating(testing, 10, context=update)

def stop_func(update, context):
    context.bot.sendMessage(chat_id=update.message.chat_id,
                      text='stopped')
    job_queue.stop()

def main():
    updater = Updater(token, use_context= True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('startapod', daily_job, pass_job_queue=True))
    dp.add_handler(CommandHandler('stopapod', stop_func, pass_job_queue=True))
    updater.start_polling()
    
if __name__ == '__main__':
    main()