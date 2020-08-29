import pandas as pd
from bs4 import BeautifulSoup as bs4
import requests
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters
import datetime
import random
import re
from better_profanity import profanity
from telegram import Bot
import pytz
import time

token =  "1183471904:AAHzW9eC9XIHJwJXRiyRKrJemA3WVxY_mug" #
bot = Bot(token)
ind_tz = pytz.timezone('Asia/Kolkata')


# --------------------- HELPER FUNCTIONS ------------------------#

def get_location(location):
    location_key_url = "http://dataservice.accuweather.com/locations/v1/cities/search?apikey=Al3vBbMBK7y8mRlkQ5ZkFu02R5NKvAGF&q="+location
    location_key_response = (requests.get(location_key_url)).json()
  
    location_info =[]
    location_info.append(str(location_key_response[0]['Key']))
    location_name = str(location_key_response[0]['EnglishName'])+", " + str(location_key_response[0]['AdministrativeArea']['EnglishName'])
    location_info.append(str(location_name))
    return(location_info)

def send_weather_update(location):
    try:
        location_info = get_location(location)
        current_weather_url = "http://dataservice.accuweather.com/currentconditions/v1/"+location_info[0]+"?apikey=Al3vBbMBK7y8mRlkQ5ZkFu02R5NKvAGF&details=true"
        current_weather_response = (requests.get(current_weather_url)).json()
        astronomy_link = re.sub("current","astronomy",current_weather_response[0]['Link'])
        html_message ="Location: "+str(location_info[1]) +"\nWeather condition: "+ str(current_weather_response[0]['WeatherText'])+"\nClouds Coverage: "+ str(current_weather_response[0]['ObstructionsToVisibility'])+"\nPercentage clouds: "+ str(current_weather_response[0]['CloudCover'])+"%\nAstronomy Consitions: <a href=\""+astronomy_link+"\">here</a>"
        return(html_message)
    except:
        return("Service unavailable.")
    

def get_weather(update, context):
    search_text=""
    for i in context.args:
        search_text += " " + i
    #bot.sendMessage(chat_id=update.message.chat_id, text = search_text)    
    bot.sendMessage(chat_id=update.message.chat_id, text = send_weather_update(search_text), parse_mode='HTML')

# ---------------------- HELPER FUNCTIONS ------------------------#






def main():
    
    updater = Updater(token, use_context= True) 
    
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('weather',get_weather, pass_args=True))
    updater.start_polling()
    #updater.idle()


if __name__ == '__main__':
    main()