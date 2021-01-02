from bs4 import BeautifulSoup as bs4
import requests
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent
import datetime
import random
import re
from better_profanity import profanity
import pytz
import time
import sys
from libgen_api import LibgenSearch
ls = LibgenSearch()



ind_tz = pytz.timezone('Asia/Kolkata')

class Helper():

    def __init__(self):
        return

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


class AstroBot():

    def __init__(self):
        self.h = Helper()

# ------------------- GENERATE RANDOM ARTICLES FROM POOL OF TOPICS ----------------------#

    def get_random_article(self):

        random_topics=['astronomy', 'latest+astronomy+news', 'astronomy+events','black+holes', 'space+exploration', 'hubble+space+telescope','space+observatory','astrophysics', 'Cosmology', 'Astrophotography'] #Topics for random article generator

        keyword = random_topics[random.randint(0,len(random_topics)-1)]
        url = "https://www.google.com/search?q="+keyword+"&source=lnms&tbm=nws&sa=X&ved=2ahUKEwjTi4TOw_7qAhWzyDgGHVjpAyYQ_AUoAXoECBUQAw&biw=1680&bih=948"
        articles_text = self.h.scrape(url)
        data = []
        for i in articles_text:
            data.append([self.h.get_article_url(i),self.h.get_time(i),i.find(class_ = "BNeawe vvjwJb AP7Wnd").contents[0]])

        return(data[random.randrange(0,len(articles_text),1)][0])

    
    #BOT CALLED FUNCTION
    def random_article(self, update, context):
        try:
            update.message.reply_text(self.get_random_article())
        except:
            update.message.reply_text("Error in retrieving data.")
            context.bot.sendMessage(chat_id="-1001331038106", text = "AstroBot error(random_article):\n" + str(sys.exc_info()))

# ----------------------------------------------------------------------------------------#

# ----------------------------------- DAILY ARTICLES -------------------------------------- #

    def send_article(self, context):
        weekly_article_topics=['astronomy', 'latest+astronomy+news', 'astronomy+events','space+observations']
        day = datetime.datetime.now().astimezone(ind_tz).strftime("%A")
        if day == 'Friday':
            topic_day = 'the+sky+this+week+site:astronomy.com'  #Astronomy magazine weekly update
        else:
            topic_day = weekly_article_topics[random.randint(0,len(weekly_article_topics)-1)] #Random article from pool of topics
        
        url = "https://www.google.com/search?q="+topic_day+"&source=lnms&tbm=nws&sa=X&ved=2ahUKEwjZzKWTjv3qAhVFyzgGHeKzCf8Q_AUoAXoECBUQAw&biw=1680&bih=947"
        #articles_text = scrape(url)
        data = []
        for i in self.h.scrape(url):
            data.append([self.h.get_article_url(i),self.h.get_time(i),i.find(class_ = "BNeawe vvjwJb AP7Wnd").contents[0]])
        data = sorted(data, key = lambda x:x[1])
        context.bot.sendMessage(chat_id = context.job.context,text = (data[0][0]))

    def get_article(self, update,context):
        job_removed= self.h.remove_job(str(update.message.chat_id), context)
        if(job_removed):
            r = context.bot.sendMessage(chat_id=update.message.chat_id, text="Running instance terminated.")
            time.sleep(10)
            context.bot.delete_message(update.message.chat_id, r.message_id)
            
        context.bot.sendMessage(chat_id = update.message.chat_id, text="Articles related to astronomy will be everyday.\n\n Clear Skies!")
        context.job_queue.run_daily(self.send_article, time = datetime.time(17,0,0,tzinfo=ind_tz), context = update.message.chat_id, name=str(update.message.chat_id))
        
    def stop_func(self, update, context):
        job_removed = self.h.remove_job(str(update.message.chat_id), context)
        if(job_removed):
            context.bot.sendMessage(chat_id=update.message.chat_id, text='Daily articles have been stopped')

# ----------------------------------------------------------------------------------------#

# ----------------------- FETCH LATEST ARTICLE BASED ON KEYWORDS BY USER --------------------------- #

    def get_keyword_articles(self, keyword):
        if(profanity.contains_profanity(keyword)):
            return "no results"
        elif(keyword==""):
            return("Please enter a keyword for search.")
        else:
            url = "https://www.google.com/search?q="+keyword+"&source=lnms&tbm=nws&sa=X&ved=2ahUKEwjTi4TOw_7qAhWzyDgGHVjpAyYQ_AUoAXoECBUQAw&biw=1680&bih=948"
            data = []
            for i in self.h.scrape(url):
                data.append([self.h.get_article_url(i),self.h.get_time(i),i.find(class_ = "BNeawe vvjwJb AP7Wnd").contents[0]])
            #data = sorted(data, key = lambda x:x[1])
            return(data) #calls function from weekly articles generator


    ''' COMMAND /news FOR ASTROBOT '''
    #def fetch_article(self, update, context):
    #    search_text=""
    #    for i in context.args:
    #        search_text = search_text + " " +i
    #    try:
    #        update.message.reply_text(self.get_keyword_article(search_text)[0][0])
    #        print(self.get_keyword_article(search_text)[0])
    #    except:
    #        update.message.reply_text("Error in retrieving data.")
    #        context.bot.sendMessage(chat_id="-1001331038106", text = "AstroBot error(fetch_article):\n" + str(sys.exc_info())) 

    def news_articles_inline(self, update, context):
        query = update.inline_query.query
        results = list()
        if not query:
            return
        print(query)
        print('_'*40)
        data = self.get_keyword_articles(query)
        #max_results = len(data) if len(data) < 5 else 5
        for i in range(len(data)):
            results.append(
                InlineQueryResultArticle(
                    id = i,
                    title = data[i][2],
                    input_message_content = InputTextMessageContent(message_text = '<a href=\''+data[i][0] + '\'>'+data[i][2]+'</a>', parse_mode= 'HTML')
                )
            )
        context.bot.answer_inline_query(update.inline_query.id, results)

# ----------------------------------------------------------------------------------------------#

# ----------------------------- WIKI SUMMARY AND LINK GENERATOR --------------------------------#
    def get_wiki_link(self, search_text):
        google_url = "https://www.google.com/search?q="+search_text+"&rlz=1C5CHFA_enIN908IN908&oq="+search_text+"&aqs=chrome.0.69i59.6224j0j1&sourceid=chrome&ie=UTF-8"
        google_page = bs4((requests.get(google_url)).text,'html.parser')
        google_page = google_page.find(class_ = "ZINbbc xpd O9g5cc uUPGi")
        wiki_link = google_page.find('a')['href'].replace('/url?q=','').split('&sa')[0]
        if(wiki_link.find('wikipedia')):
            if(wiki_link.find("%25")):   #addressing issue with links that contain '%25'
                wiki_link = re.sub("%25","%", wiki_link)
            return(wiki_link)
        else:
            return("Cannot find Wikipedia link.")
    
    def scrape_wiki(self, search_text, context):
        if(profanity.contains_profanity(search_text)):
            return("censored.")
        elif(search_text == '+site:wikipedia.org'):
            return("Please include keyword for search.")
        else:
            try:
                wiki_link = self.get_wiki_link(search_text)
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
                
    
    def get_wiki_info(self, update, context):
        search_text=""
        for i in context.args:
            search_text = search_text + " " +i
        search_text += "+site:wikipedia.org"
        update.message.reply_text(self.scrape_wiki(search_text.lower()))

# ----------------------------------------------------------------------------------------------#

# ------------------------------------ WEATHER UPDATES --------------------------------------#

    def get_moon_info(self):
        td_url = "https://www.timeanddate.com/moon/phases/india/hyderabad"
        td_response = requests.get(td_url)
        td_response = bs4(td_response.text, 'html.parser')
        moon_image = "https://www.timeanddate.com/" + str(td_response.find(id='cur-moon')['src'])
        moon_percent = td_response.find(id='cur-moon-percent').text
        moon_phase = td_response.findAll('section',{'class':'bk-focus'})[0].find('a').text
        return moon_image, moon_percent, moon_phase

    def bortle_info(self, lat, lon):
        url = "https://clearoutside.com/forecast/"+str(lat)+"/"+str(lon)
        #bortle = bs4(requests.get(url).text, 'html.parser')
        info = []
        for i in bs4(requests.get(url).text, 'html.parser').find('span', class_ = 'btn-primary').findAll('strong'):
            info.append(i.text)
        bortle_info = "Bortle " + info[1] + "\nSQM: " + info[0] + "\nArtificial Brightness: " + info[3] + "μcd/m2"
        return bortle_info


    def weather_data(self, lat, lon, search_data):
        
        openweather_url = "https://api.openweathermap.org/data/2.5/onecall?lat="+str(lat)+"&lon="+str(lon)+"&exclude=minutely&units=metric"+"&appid=90701b1aba6e661af014c16e653b91c3"
        openweather_response = (requests.get(openweather_url)).json()
        
        sunset_time = datetime.datetime.fromtimestamp(int(openweather_response['current']['sunset'])).astimezone(ind_tz).time()
        current_time = datetime.datetime.fromtimestamp(int(openweather_response['current']['dt'])).astimezone(ind_tz).time()
        cloud_cover = openweather_response['current']['clouds']
        wind_speed = round(float(openweather_response['current']['wind_speed']*18/5),2)
        description = openweather_response['current']['weather'][0]['description']
        dew_point  = openweather_response['current']['dew_point']
        temperature  = openweather_response['current']['temp']
        moon_image, moon_percent, moon_phase = self.get_moon_info()
    
        #weather_message = "Weather update for "+search_data+ "at " + str(current_time) +"\nStatus: "+description+"\nCloud Cover: "+str(cloud_cover)+"%\nWind Speed: "+str(wind_speed)+"kmph\nTemperature: "+str(temperature)+"°C\n--------------------\nMoon Illumination: "+moon_percent+"\nMoon Phase: "+moon_phase
        weather_message = "\nStatus: "+description+"\nCloud Cover: "+str(cloud_cover)+"%\nWind Speed: "+str(wind_speed)+"kmph\nTemperature: "+str(temperature)+"°C\nDew Point: "+str(dew_point)+"°C\n————————————\nMoon Illumination: "+moon_percent+"\nMoon Phase: "+moon_phase
        return weather_message, moon_image
        
    
    def get_weather(self, update, context):
        search_text=""
        for i in context.args:
            search_text += i + ' '
            
        if(re.search("^[0-9]",search_text)):
            lat, lon = search_text.replace(' ','').split(',')
        elif (search_text==''):
            context.bot.sendMessage(chat_id=update.message.chat_id, text='Please include a location.')
            return
        else:
            lat, lon = self.h.get_coordintes(search_text)
            
            
        try:    
            weather_message, moon_photo = self.weather_data(lat, lon, search_text)
            bortle_info = self.bortle_info(lat, lon)
            context.bot.sendPhoto(chat_id=update.message.chat_id, caption = weather_message +"\n————————————\n"+ bortle_info, photo=moon_photo)
            #context.bot.sendMessage(chat_id=update.message.chat_id, text=bortle_info)
        except:
            context.bot.sendMessage(chat_id=update.message.chat_id, text="Error in retrieving data.")
            context.bot.sendMessage(chat_id="-1001331038106", text = "AstroBot error(get_weather):\n" + str(sys.exc_info()))

# ----------------------------------------------------------------------------------------------#


    def get_book_download_link(self,url):
        #r = requests.get(url)
        page = bs4((requests.get(url)).text, 'html.parser')
        link = page.find('div', id='download').findAll('a')[1].attrs['href']
        alt_link = page.find('div', id='download').findAll('a')[0].attrs['href']
        return link, alt_link

    def get_book_cover_img(self, url):
        page = bs4((requests.get(url)).text, 'html.parser')
        img_url = 'http://library.lol/' + page.find('img').attrs['src']
        return img_url

    '''INLINE FEATURE FOR BOOKS'''

    def send_book(self, update, context):
        s = time.time()
        query = update.inline_query.query
        filters = {'Extension':'pdf'}
        results = list()
        if not query:
            return
        print(query)
        print('_'*40)
        books = ls.search_title_filtered(query, filters)
        max_results = len(books) if len(books) < 5 else 5
        for i in range(max_results):
            results.append(
                InlineQueryResultArticle(
                    id = books[i]['ID'],
                    title = books[i]['Title'] + ' by ' + books[i]['Author'],
                    input_message_content = InputTextMessageContent(message_text = '<a href=\''+self.get_book_download_link(books[i]['Mirror_1'])[0] + '\'>'+books[i]['Title'] + ' by ' + books[i]['Author']+'</a>', parse_mode= 'HTML')
                    #url = self.get_book_cover_img(books[i]['Mirror_1'])
                )
            )
        e = time.time()
        print(e-s)
        context.bot.answer_inline_query(update.inline_query.id, results)


    def new_books(self, update, context):
        filters = {'Extension':'pdf'}
        search_text = ''
        for i in context.args:
            search_text += i + ' '
        params = search_text.split(' by ')
        if len(params) == 2:
            books = ls.search_title_filtered(params[0].strip().lower(), filters)
            for book in books:
                if book['Author'].strip().lower() == params[1].strip().lower():
                    link, alt_link = self.get_book_download_link(book['Mirror_1'])
                    title = book['Title']
                    author = book['Author']
                    break
        else:
            books = ls.search_title_filtered(params[0].strip().lower(), filters)
            link, alt_link= self.get_book_download_link(books[0]['Mirror_1'])
            title = books[0]['Title']
            author = books[0]['Author']
        try:
            context.bot.send_document(chat_id = update.message.chat_id, document= link, filename=str(title+'by'+author), caption = str(title+' by '+author))
        except:
            print(str(sys.exc_info()))
            context.bot.sendMessage(chat_id = update.message.chat_id, text = '<a href=\''+link + '\'>'+title + ' by ' + author+'</a>', parse_mode='HTML')
            alternate = context.bot.sendMessage(chat_id = update.message.chat_id, text = 'This an alternate download link for the book:\n\n<a href=\''+alt_link + '\'>'+title + ' by ' + author+'</a>\n\n auto-deletes in 30 seconds', parse_mode='HTML')
            time.sleep(30)
            context.bot.delete_message(update.message.chat_id, alternate.message_id)



# ------------------------------------ WELCOME NEW MEMBERS -------------------------------------#

    def welcome_new_user(self, update, context):
        for new_user_obj in update.message.new_chat_members:
            chat_id = update.message.chat_id
            new_usr = ""
            message=r"Welcome to Hyderabad Astronomy Club $user! Please introduce yourself and tell us what you're interested in." # Welcome message
            try:
                new_usr = '@' + new_user_obj['username']
            except:
                new_usr = new_user_obj['first_name']
        context.bot.sendMessage(chat_id, text = message.replace('$user',new_usr))


# ----------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------------------#


    def bot_help(self, update, context):
        help_text = "Hello, these are the commands I will respond to:\n\nTyping \"/randomarticle\" will fetch a random article related to an astronomy subject.\n\nTyping \"/wiki <keyword>\" will produce a short summary and link to wikipedia\n\nTyping \"/weather <latitude, longitude>\" or \"/weather <location name>\" will fetch a weather update.\n\nTyping \"/book <bookname>\" will fetch the PDF version of the book from Library Genesis (May not find every book)\n\nIf you are looking for a news article use \"@HAC_AstroBot <search query>\"\n\nTyping \"/help\" will show you all the current list of commands I can respond to."
        update.message.reply_text(help_text)



    