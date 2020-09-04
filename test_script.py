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

token =  "1183471904:AAHzW9eC9XIHJwJXRiyRKrJemA3WVxY_mug"
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

def weather_data(lat, lon):
    openweather_url = "https://api.openweathermap.org/data/2.5/onecall?lat="+str(lat)+"&lon="+str(lon)+"&exclude=minutely&units=metric"+"&appid=90701b1aba6e661af014c16e653b91c3"
    openweather_response = (requests.get(openweather_url)).json()
    clearoutside_image = "https://clearoutside.com/forecast_image_medium/"+str(round(lat,2))+"/"+str(round(lon,2))+"/forecast.png"
    sunset_time = datetime.fromtimestamp(int(openweather_response['current']['sunset'])).time()
    cloud_cover = openweather_response['current']['clouds']
    wind_speed = round(float(openweather_response['current']['wind_speed']*18/5),2)
    description = openweather_response['current']['weather'][0]['description']
    dew_point  = openweather_response['current']['dew_point']
    temperature  = openweather_response['current']['temp']
    icon_url = "http://openweathermap.org/img/wn/"+openweather_response['current']['weather'][0]['icon']+"@2x.png"
    moon_image, moon_percent, moon_phase = get_moon_info()
    #"Weather update for "+str(lat)+", "+str(lon)+ 
    html_message = "Weather update for <b>"+str(round(lat,2))+", "+str(round(lon,2))+"\nStatus:</b> "+description+"\n<b>Cloud cover: </b>"+str(cloud_cover)+"%\n<b>Wind speed:</b> "+str(wind_speed)+"kmph\n<b>Dew Point:</b> "+str(dew_point)+"°C\n<b>Temperature:</b> "+str(temperature)+"°C\n<b>Moon Illumination:</b> "+moon_percent+"\n<b>Moon phase:</b> "+moon_phase
    message = "Weather update for "+str(round(lat,2))+", "+str(round(lon,2))+"\nStatus: "+description+"\nCloud cover: "+str(cloud_cover)+"%\nWind speed: "+str(wind_speed)+"kmph\nTemperature: "+str(temperature)+"°C\nDew Point: "+str(dew_point)+"°C\nMoon Illumination: "+moon_percent+"\nMoon phase: "+moon_phase
    return message, moon_image, clearoutside_image
    

def get_weather(update, context):
    search_text=""
    for i in context.args:
        search_text += i
    #bot.sendMessage(chat_id=update.message.chat_id, text = search_text)    
    if(re.search("^[0-9]",search_text)):
        lat, lon = search_text.replace(' ','').split(',')
    else:
        geolocation_url = "https://dev.virtualearth.net/REST/v1/Locations?key=Al3NnfvA47J04pxm1b6YfknCea0TYqx4TuzYQJ_EnCXTb5N8ZLMwPtrB631UHiJJ&o=json&q="+search_text+"&jsonso="+search_text
        geolocation_response = (requests.get(geolocation_url)).json()
        lat, lon = geolocation_response['resourceSets'][0]['resources'][0]['point']['coordinates']
    try:    
        message, moon_photo, cl_image = weather_data(lat, lon)
        context.bot.sendPhoto(chat_id=update.message.chat_id, caption = message, photo=cl_image)
        #context.bot.sendMessage(chat_id="-1001331038106", text = str(lat) + ", "+str(lon))
    except:
        context.bot.sendMessage(chat_id=update.message.chat_id, text="Error in retrieving data.")
        contex.bot.sendMessage(chat_id="-1001331038106", text = "AstroBot error(scrape_wiki):\n" + str(sys.exc_info()))

# ---------------------- HELPER FUNCTIONS ------------------------#

def main():
    
    updater = Updater(token, use_context= True) 
    
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('weather',get_weather, pass_args=True))
    updater.start_polling()
    #updater.idle()


if __name__ == '__main__':
    main()