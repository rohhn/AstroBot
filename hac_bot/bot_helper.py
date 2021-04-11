from bs4 import BeautifulSoup as bs4
import requests
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup

class Helper():

    def __init__(self):
        self.astrobot_help = "Commands for @HAC_AstroBot:\n\n/randomarticle - Fetch a random article related to an astronomy subject.\n\n/wiki <keyword> - Generate a short summary and link to wikipedia.\n\n/weather <latitude, longitude> or\n/weather <location name> or\nsending a map location - Fetch a weather update.\n\n/news <search phrase> - search for related articles on Google News.\n\n/help - Display all bot commands."
        self.photobot_help = "Commands for @HAC_PhotoBot:\n\n/analyze or /analyse - Plate-solve an astronomy image.\n\nAsk the bot information about any DSO by typing \"@HAC_PhotoBot tell me about <DSO Name>\""
        self.bookbot_help = "Commands for @LibgenLibrary_Bot:\n\n/book <bookname> - Search for the book title on Library Genesis."
        #Commands for @HAC_PhotoBot:\n\n/

    def remove_job(self, name, context):
        cur_jobs = context.job_queue.get_jobs_by_name(name)
        if not cur_jobs:
            return False
        for job in cur_jobs:
            job.schedule_removal()
        return True

    def scrape(self, url):
        page  = requests.get(url) 
        page_text = bs4(page.text,'html.parser') # parse google news page to find all articles
        articles_text = page_text.find_all(class_ = "ZINbbc xpd O9g5cc uUPGi")
        return articles_text #return list of all articles

    def get_article_url(self, url):
        url = url.find('a').attrs['href'].replace('/url?q=','').split('&sa')[0]
        return url

    def get_time(self, i): 
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
        else:
            time_since = 9999999
        return(time_since) #return time since posted

    def get_coordintes(self, search_text):
        geolocation_url = "https://dev.virtualearth.net/REST/v1/Locations?key=Al3NnfvA47J04pxm1b6YfknCea0TYqx4TuzYQJ_EnCXTb5N8ZLMwPtrB631UHiJJ&o=json&q="+search_text+"&jsonso="+search_text
        geolocation_response = (requests.get(geolocation_url)).json()
        lat = round(geolocation_response['resourceSets'][0]['resources'][0]['point']['coordinates'][0],2)
        lon = round(geolocation_response['resourceSets'][0]['resources'][0]['point']['coordinates'][1],2)
        return lat, lon