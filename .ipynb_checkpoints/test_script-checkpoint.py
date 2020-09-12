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
import sys
from streamlit import caching

token ="1183471904:AAHzW9eC9XIHJwJXRiyRKrJemA3WVxY_mug"  #'1222703294:AAFtKTZoWytkkt9ZUFehhbwuUrYyzzlitUU' 
bot = Bot(token)
ind_tz = pytz.timezone('Asia/Kolkata')


# --------------------- HELPER FUNCTIONS ------------------------#
def scrape(url):
    #parse html text of the google news page url
    page  = requests.get(url)
    page_text = bs4(page.text,'html.parser')
    articles_text = page_text.find_all(class_ = "ZINbbc xpd O9g5cc uUPGi")
    #create list of articles
    return articles_text

def get_article_url(url):
    #
    url = url.find('a').attrs['href'].replace('/url?q=','')
    url = url.split("&sa")[0]
    return url

def get_time(i):
    posted_time = i.find(class_ = "r0bn4c rQMQod").contents[0]
    posted_time = posted_time.split(" ")
    if (posted_time[1] == 'mins' or posted_time[1] == 'min'):
        time_since = int(posted_time[0])
    if (posted_time[1] == 'hours' or posted_time[1] == 'hour'):
        time_since = 60 * int(posted_time[0])
    elif (posted_time[1] == 'days' or posted_time[1] == 'day'):
        time_since = 24*60 * int(posted_time[0])
    elif (posted_time[1] == 'weeks' or posted_time[1] == 'week'):
        time_since = 7*24*60* int(posted_time[0])
    #elif (posted_time[1] == 'months' or posted_time[1] == 'month'):
    #    time_since = 100* int(posted_time[0])
    else:
        time_since = 9999999
    return(time_since)

# ---------------------- HELPER FUNCTIONS ------------------------#



# ------------------- GENERATE RANDOM ARTICLES FROM POOL OF TOPICS ----------------------#

#Topics for random article generator


def get_final_random_article(articles_text):
    data = []
    for i in articles_text: 
        data.append([get_article_url(i),get_time(i),i.find(class_ = "BNeawe vvjwJb AP7Wnd").contents[0]])
    data = sorted(data, key = lambda x: x[1])
    i = random.randrange(0,len(articles_text),1)
    return(data[i][0])

def get_random_article():
    random_topics=['astronomy', 'latest+astronomy+news', 'astronomy+events','black+holes', 'space+exploration', 'hubble+space+telescope','space+observatory','astrophysics', 'Cosmology', 'Astrophotography']
    i = random.randrange(0,len(random_topics),1)
    keyword = random_topics[i]
    url = "https://www.google.com/search?q="+keyword+"&source=lnms&tbm=nws&sa=X&ved=2ahUKEwjTi4TOw_7qAhWzyDgGHVjpAyYQ_AUoAXoECBUQAw&biw=1680&bih=948"
    articles_text = scrape(url)
    return(get_final_random_article(articles_text))

#BOT CALLED FUNCTION
def random_article(update, context):
    try:
        update.message.reply_text(get_random_article())
    except:
        update.message.reply_text("Error in retrieving data.")
        context.bot.sendMessage(chat_id="-1001331038106", text = "AstroBot error(random_article):\n" + str(sys.exc_info()))

# ----------------------------------------------------------------------------------------#

# ------------- GENERATE 3 ARTICLES PER WEEK (SUNDAY, WEDNESDAY, FRIDAY) ---------------- #



def get_final_article(articles_text):
    data = []
    for i in articles_text: 
        data.append([get_article_url(i),get_time(i),i.find(class_ = "BNeawe vvjwJb AP7Wnd").contents[0]])
    data = sorted(data, key = lambda x: x[1])
    return(data[0][0])

def send_article(context):
    weekly_article_topics=['astronomy', 'latest+astronomy+news', 'astronomy+events']
    day = datetime.datetime.now().astimezone(ind_tz).strftime("%A")
    #context.bot.sendMessage(chat_id = context.job.context,text = day)
    #time = int(datetime.datetime.now().strftime("%H"))
   # try:
    if day == 'Sunday':
        topic_day = weekly_article_topics[0]
    elif day == 'Wednesday':
        topic_day = weekly_article_topics[1]
    elif day == 'Friday':
        topic_day = weekly_article_topics[2] 
    url = "https://www.google.com/search?q="+topic_day+"&source=lnms&tbm=nws&sa=X&ved=2ahUKEwjZzKWTjv3qAhVFyzgGHeKzCf8Q_AUoAXoECBUQAw&biw=1680&bih=947"
    articles_text = scrape(url)
    context.bot.sendMessage(chat_id = context.job.context,text = (day + "\'s article:\n\n" + get_final_article(articles_text)))
   # except:
   #     context.bot.sendMessage(chat_id="-1001331038106", text="Error in weekly articles")
    


def get_article(update,context):
    context.bot.sendMessage(chat_id = update.message.chat_id, text="Articles will be posted on Sunday, Wednesday and Friday.\n\n Clear Skies!")
    context.job_queue.run_daily(send_article, time = datetime.time(17,23,0,tzinfo=ind_tz),days=(2,4,6), context = update.message.chat_id)
    
def stop_func(update, context):
    context.bot.sendMessage(chat_id=update.message.chat_id, text='stopped')
    job_queue.stop()



# --------------------------------------------------------------------------------------------#

# ----------------------- FETCH ARTICLE BASED ON KEYWORDS BY USER --------------------------- #
def get_keyword_article(keyword):
    if(profanity.contains_profanity(keyword)):
        return "no results"
    elif(keyword==""):
        return("Please enter a keyword for search.")
    else:
        #keyword = keyword.replace(" ","+")
        url = "https://www.google.com/search?q="+keyword+"&source=lnms&tbm=nws&sa=X&ved=2ahUKEwjTi4TOw_7qAhWzyDgGHVjpAyYQ_AUoAXoECBUQAw&biw=1680&bih=948"
        articles_text = scrape(url)
        return(get_final_article(articles_text))
        #return url

def fetch_article(update, context):
    chat_id = update.message.chat_id
    search_text=""
    for i in context.args:
        search_text = search_text + " " +i
    try:
        update.message.reply_text(get_keyword_article(search_text))
    except:
        update.message.reply_text("Error in retrieving data.")
        context.bot.sendMessage(chat_id="-1001331038106", text = "AstroBot error(fetch_article):\n" + str(sys.exc_info()))
    
#calls same function as weekly article generator    

# ----------------------------------------------------------------------------------------------#


# ----------------------------- WIKI SUMMARY AND LINK GENERATOR --------------------------------#
def get_wiki_link(search_text):
    google_url = "https://www.google.com/search?q="+search_text+"&rlz=1C5CHFA_enIN908IN908&oq="+search_text+"&aqs=chrome.0.69i59.6224j0j1&sourceid=chrome&ie=UTF-8"
    google_page = requests.get(google_url)
    google_page = bs4(google_page.text,'html.parser')
    google_page = google_page.find(class_ = "ZINbbc xpd O9g5cc uUPGi")
    wiki_link = google_page.find('a')['href'].replace('/url?q=','')
    wiki_link = wiki_link.split("&sa")[0]
    if(wiki_link.find('wikipedia')):
        if(wiki_link.find("%25")):
            wiki_link = re.sub("%25","%", wiki_link)
        return(wiki_link)
    else:
        return("Cannot find Wikipedia link.")
    
def scrape_wiki(search_text):
    if(profanity.contains_profanity(search_text)):
        return("censored.")
    elif(search_text == '+wiki'):
        return("Please include keyword for search.")
    else:
        try:
            wiki_link = get_wiki_link(search_text)
            wiki_page = requests.get(wiki_link)
            wiki_page = bs4(wiki_page.text,'html.parser')
            summary = wiki_page.find_all('p')
            summary_text=""
            for i in summary:
                if(len(i.get_text()) > 30):
                    summary_text = i.get_text()
                    break
            #image_url = "https://en.wikipedia.org"+ wiki_page.find('table').find('a')['href']
            text = summary_text + "\n\n" + wiki_link
            return(text)
        except:
            context.bot.sendMessage(chat_id="-1001331038106", text = "AstroBot error(scrape_wiki):\n" + str(sys.exc_info()))
            return("Cannot find Wikipedia page.")
            

def get_wiki_info(update, context):
    chat_id = update.message.chat_id
    search_text=""
    for i in context.args:
        search_text = search_text + " " +i
    search_text += "+wiki"
    update.message.reply_text(scrape_wiki(search_text.lower()))

# ----------------------------------------------------------------------------------------------#

# ------------------------------------ WEATHER UPDATES --------------------------------------#

def get_moon_info():
    td_url = "https://www.timeanddate.com/moon/phases/india/hyderabad"
    td_response = requests.get(td_url)
    td_response = bs4(td_response.text, 'html.parser')
    moon_image = "https://www.timeanddate.com/" + str(td_response.find(id='cur-moon')['src'])
    moon_percent = td_response.find(id='cur-moon-percent').text
    moon_phase = td_response.findAll('section',{'class':'bk-focus'})[0].find('a').text
    return moon_image, moon_percent, moon_phase

def weather_data(lat, lon, search_data):
    openweather_url = "https://api.openweathermap.org/data/2.5/onecall?lat="+str(lat)+"&lon="+str(lon)+"&exclude=minutely&units=metric"+"&appid=90701b1aba6e661af014c16e653b91c3"
    openweather_response = (requests.get(openweather_url)).json()
    clearoutside_image = "https://clearoutside.com/forecast_image_medium/"+str(lat)+"/"+str(lon)+"/forecast.png"
    sunset_time = datetime.datetime.fromtimestamp(int(openweather_response['current']['sunset'])).time()
    time = datetime.datetime.fromtimestamp(int(openweather_response['current']['dt'])).time()
    cloud_cover = openweather_response['current']['clouds']
    wind_speed = round(float(openweather_response['current']['wind_speed']*18/5),2)
    description = openweather_response['current']['weather'][0]['description']
    dew_point  = openweather_response['current']['dew_point']
    temperature  = openweather_response['current']['temp']
    icon_url = "http://openweathermap.org/img/wn/"+openweather_response['current']['weather'][0]['icon']+"@2x.png"
    moon_image, moon_percent, moon_phase = get_moon_info()
    
    #message = str(time)
    message = "Weather update for "+search_data+ "at " + str(time) +"\nStatus: "+description+"\nCloud cover: "+str(cloud_cover)+"%\nWind speed: "+str(wind_speed)+"kmph\nTemperature: "+str(temperature)+"°C\nDew Point: "+str(dew_point)+"°C\nMoon Illumination: "+moon_percent+"\nMoon phase: "+moon_phase
    return message, moon_image, clearoutside_image
    

def get_weather(update, context):
    search_text=""
    for i in context.args:
        search_text += i + ' '
    #bot.sendMessage(chat_id=update.message.chat_id, text = search_text)    
    if(re.search("^[0-9]",search_text)):
        lat, lon = search_text.replace(' ','').split(',')
    else:
        geolocation_url = "https://dev.virtualearth.net/REST/v1/Locations?key=Al3NnfvA47J04pxm1b6YfknCea0TYqx4TuzYQJ_EnCXTb5N8ZLMwPtrB631UHiJJ&o=json&q="+search_text+"&jsonso="+search_text
        geolocation_response = (requests.get(geolocation_url)).json()
        lat = round(geolocation_response['resourceSets'][0]['resources'][0]['point']['coordinates'][0],2)
        lon = round(geolocation_response['resourceSets'][0]['resources'][0]['point']['coordinates'][1],2)
        
    try:    
        message, moon_photo, cl_image = weather_data(lat, lon, search_text)
        context.bot.sendPhoto(chat_id=update.message.chat_id, caption = message, photo=moon_photo)
        #caching.clear_cache()
        #context.bot.sendMessage(chat_id="-1001331038106", text = str(lat) + ", "+str(lon))
    except:
        context.bot.sendMessage(chat_id=update.message.chat_id, text="Error in retrieving data.")
        #print(str(sys.exc_info()))
        context.bot.sendMessage(chat_id="-1001331038106", text = "AstroBot error(get_weather):\n" + str(sys.exc_info()))

# ----------------------------------------------------------------------------------------------#


# ------------------------------------ PRINT HELP COMMANDS -------------------------------------#
def bot_help(update, context):
    chat_id = update.message.chat_id
    help_text = "Hello, these are the commands I will respond to:\n\nTyping \"/randomarticle\" will fetch a random article related to an astronomy subject.\n\nTyping \"/newarticle <keyword>\" will fetch an article related to the keyword.\n\nTyping \"/wiki <keyword>\" will produce a short summary and link to wikipedia\n\nTyping \"/weather <latitude, longitude>\" or \"/weather <location name>\" will fetch a weather update.\n\nTyping \"/help\" will show you all the current list of commands I can respond to."
    update.message.reply_text(help_text)
    
# ----------------------------------------------------------------------------------------------#



def main():
    caching.clear_cache()
    updater = Updater(token, use_context= True) 
    
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('weekly_articles',get_article, pass_job_queue = True))
    dp.add_handler(CommandHandler('stop_weekly_articles',stop_func, pass_job_queue = True))
    dp.add_handler(CommandHandler('randomarticle',random_article))
    dp.add_handler(CommandHandler('help',bot_help))
    dp.add_handler(CommandHandler('newarticle', fetch_article, pass_args=True))
    dp.add_handler(CommandHandler('wiki',get_wiki_info, pass_args=True))
    dp.add_handler(CommandHandler('weather',get_weather, pass_args=True))
    caching.clear_cache()
    updater.start_polling()
    #updater.idle()


if __name__ == '__main__':
    main()