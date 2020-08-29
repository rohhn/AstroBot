import pandas as pd
from bs4 import BeautifulSoup as bs4
import requests
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters
from datetime import datetime
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
 
def get_moon_info():
    td_url = "https://www.timeanddate.com/moon/phases/india/hyderabad"
    td_response = requests.get(td_url)
    td_response = bs4(td_response.text, 'html.parser')
    moon_image = "https://www.timeanddate.com/" + str(td_response.find(id='cur-moon')['src'])
    moon_percent = td_response.find(id='cur-moon-percent').text
    moon_phase = td_response.findAll('section',{'class':'bk-focus'})[0].find('a').text
    return moon_image, moon_percent, moon_phase

def openweather(lat, lon):
    openweather_api = "90701b1aba6e661af014c16e653b91c3"
    openweather_url = "https://api.openweathermap.org/data/2.5/onecall?lat="+lat+"&lon="+lon+"&exclude=minutely&units=metric"+"&appid="+openweather_api
    openweather_response = (requests.get(openweather_url)).json()
    latitude = openweather_response['lat']
    longitude = openweather_response['lon']
    sunset_time = datetime.fromtimestamp(int(openweather_response['current']['sunset'])).time()
    cloud_cover = openweather_response['current']['clouds']
    wind_speed = round(float(openweather_response['current']['wind_speed']*18/5),2)
    description = openweather_response['current']['weather'][0]['description']
    icon_url = "http://openweathermap.org/img/wn/"+openweather_response['current']['weather'][0]['icon']+"@2x.png"
    moon_image, moon_percent, moon_phase = get_moon_info()
    message = "Weather update for "+str(latitude)+", "+str(longitude)+ "\nCloud cover: "+str(cloud_cover)+"%\nWind speed: "+str(wind_speed)+"kmph\nStatus: "+description+"\nMoon Illumination: "+moon_percent+"\nMoon phase: "+moon_phase
    return message, moon_image
    

def get_weather(update, context):
    search_text=""
    for i in context.args:
        search_text += i
    #bot.sendMessage(chat_id=update.message.chat_id, text = search_text)    
    lat, lon = search_text.replace(' ','').split(',')
    message, photo = openweather(lat, lon)
    context.bot.sendPhoto(chat_id=update.message.chat_id, caption = message, photo=photo)

# ---------------------- HELPER FUNCTIONS ------------------------#

def main():
    
    updater = Updater(token, use_context= True) 
    
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('weather',get_weather, pass_args=True))
    updater.start_polling()
    #updater.idle()


if __name__ == '__main__':
    main()