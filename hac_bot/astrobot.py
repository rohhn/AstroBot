import re, os, sys, random, time, pytz, requests
from bs4 import BeautifulSoup as bs4
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
import datetime
from better_profanity import profanity
from libgen_api import LibgenSearch
ls = LibgenSearch()
from hac_bot.bot_helper import Helper
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
from PIL import Image

ind_tz = pytz.timezone('Asia/Kolkata')

if os.environ['DEPLOYMENT_ENVIRONMENT'] == 'DEV':
    chromedriver_path = '/Users/rohan/Desktop/projects/bot_env/bin/chromedriver'
    openweather_key = open('config/openweather_key.conf','r').read()
elif os.environ['DEPLOYMENT_ENVIRONMENT'] == 'PROD':
    chromedriver_path = '/var/lib/chromedriver'
    openweather_key = os.environ['OPENWEATHER_KEY']
else:
    print("Development Environment not known. Check Environment variable - DEPLOYMENT_ENVIRONMENT")
    exit()


class AstroBot():

    def __init__(self):
        self._helper = Helper()

# ------------------- GENERATE RANDOM ARTICLES FROM POOL OF TOPICS ----------------------#

    def get_random_article(self):

        random_topics=['astronomy', 'latest+astronomy+news', 'astronomy+events','black+holes', 'space+exploration', 'hubble+space+telescope','space+observatory','astrophysics', 'Cosmology', 'Astrophotography'] #Topics for random article generator

        keyword = random_topics[random.randint(0,len(random_topics)-1)]
        url = "https://www.google.com/search?q="+keyword+"&source=lnms&tbm=nws&sa=X&ved=2ahUKEwjTi4TOw_7qAhWzyDgGHVjpAyYQ_AUoAXoECBUQAw&biw=1680&bih=948"
        articles_text = self._helper.scrape(url)
        data = []
        for i in articles_text:
            data.append([self._helper.get_article_url(i),self._helper.get_time(i),i.find(class_ = "BNeawe vvjwJb AP7Wnd").contents[0]])

        return(data[random.randrange(0,len(articles_text),1)][0])

    
    # /randomarticle
    def send_random_article(self, update, context):
        try:
            update.message.reply_text(self.get_random_article())
        except:
            update.message.reply_text("Error in retrieving data.")
            # context.bot.sendMessage(chat_id=str(os.environ["HAC_TEST_CHAT"]), text = "AstroBot error(random_article):\n" + str(sys.exc_info()))

# ----------------------------------------------------------------------------------------#

# ----------------------------------- DAILY ARTICLES -------------------------------------- #

    def get_daily_article(self, context):
        weekly_article_topics=['astronomy', 'latest+astronomy+news', 'astronomy+events','space+observations']
        day = datetime.datetime.now().astimezone(ind_tz).strftime("%A")
        if day == 'Friday':
            topic_day = 'the+sky+this+week+site:astronomy.com'  #Astronomy magazine weekly update
        else:
            topic_day = weekly_article_topics[random.randint(0,len(weekly_article_topics)-1)] #Random article from pool of topics
        
        url = "https://www.google.com/search?q="+topic_day+"&source=lnms&tbm=nws&sa=X&ved=2ahUKEwjZzKWTjv3qAhVFyzgGHeKzCf8Q_AUoAXoECBUQAw&biw=1680&bih=947"
        #articles_text = scrape(url)
        data = []
        for i in self._helper.scrape(url):
            data.append([self._helper.get_article_url(i),self._helper.get_time(i),i.find(class_ = "BNeawe vvjwJb AP7Wnd").contents[0]])
        data = sorted(data, key = lambda x:x[1])
        context.bot.sendMessage(chat_id = context.job.context,text = (data[0][0]))


    # /daily_articles
    def send_daily_article(self, update,context):
        job_removed= self._helper.remove_job(str(update.message.chat_id), context)
        if(job_removed):
            r = context.bot.sendMessage(chat_id=update.message.chat_id, text="Running instance terminated.")
            context.bot.delete_message(update.message.chat_id, r.message_id)
            
        context.bot.sendMessage(chat_id = update.message.chat_id, text="Articles related to astronomy will be everyday.\n\n Clear Skies!")
        context.job_queue.run_daily(self.get_daily_article, time = datetime.time(17,0,0,tzinfo=ind_tz), context = update.message.chat_id, name=str(update.message.chat_id))
  

    # /stop_daily_articles    
    def stop_daily_article(self, update, context):
        job_removed = self._helper.remove_job(str(update.message.chat_id), context)
        if(job_removed):
            context.bot.sendMessage(chat_id=update.message.chat_id, text='Daily articles have been stopped.')

# ----------------------------------------------------------------------------------------#

# ----------------------- FETCH NEWS ARTICLES BASED ON KEYWORDS BY USER --------------------------- #

    def get_news_articles_by_keyword(self, keyword):
        if(profanity.contains_profanity(keyword)):
            return False
        elif(keyword==""):
            return False
        else:
            try:
                url = "https://www.google.com/search?q="+keyword+"&source=lnms&tbm=nws&sa=X&ved=2ahUKEwjTi4TOw_7qAhWzyDgGHVjpAyYQ_AUoAXoECBUQAw&biw=1680&bih=948"
                data = []
                for i in self._helper.scrape(url):
                    data.append([self._helper.get_article_url(i),self._helper.get_time(i),i.find(class_ = "BNeawe vvjwJb AP7Wnd").contents[0]])
                return(data)
            except:
                return False


    def send_inline_news(self, update, context):
        query = update.inline_query.query
        results = list()
        if not query:
            return
        data = self.get_news_articles_by_keyword(query)
        if data:
            for i in range(len(data)):
                results.append(
                    InlineQueryResultArticle(
                        id = i,
                        title = data[i][2],
                        input_message_content = InputTextMessageContent(message_text = '<a href=\''+data[i][0] + '\'>'+data[i][2]+'</a>', parse_mode= 'HTML')
                    )
                )
        else:
            results.append(
                InlineQueryResultArticle(
                    id="0",
                    title='No results found',
                    input_message_content= InputTextMessageContent(message_text="No results found")))

        context.bot.answer_inline_query(update.inline_query.id, results)
        context.bot.delete_message(chat_id=self.x.chat.id, message_id = self.x.message_id)


    # /news
    def send_news_article(self, update, context):
        search_text=""
        for i in context.args:
            search_text = search_text + " " +i
        try:
            kb_list = [[InlineKeyboardButton(text='Search', switch_inline_query_current_chat=search_text.strip())]]
            kb = InlineKeyboardMarkup(kb_list)
            self.x= update.message.reply_text(text=search_text.strip(), reply_markup = kb)
        except:
            kb_list = [[InlineKeyboardButton(text='Search', switch_inline_query_current_chat="")]]
            kb = InlineKeyboardMarkup(kb_list)
            self.x= update.message.reply_text(text='Click the button to search', reply_markup = kb)

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
 
  
    def get_wiki_summary(self, search_text):
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
                return("Cannot find Wikipedia page.")
                
    
    def send_wiki_info(self, update, context):
        search_text=""
        for i in context.args:
            search_text = search_text + " " +i
        search_text += "+site:wikipedia.org"
        update.message.reply_text(self.get_wiki_summary(search_text.lower()))

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


    def get_bortle_info(self, lat, lon):
        url = "https://clearoutside.com/forecast/"+str(lat)+"/"+str(lon)
        #bortle = bs4(requests.get(url).text, 'html.parser')
        info = []
        for i in bs4(requests.get(url).text, 'html.parser').find('span', class_ = 'btn-primary').findAll('strong'):
            info.append(i.text)
        bortle_info = "Bortle " + info[1] + "\nSQM: " + info[0] + "\nArtificial Brightness: " + info[3] + "μcd/m2"
        return bortle_info


    def get_lp_img(self, lat, lon):
        try:
            if os.environ['DEPLOYMENT_ENVIRONMENT'] == 'DEV':
                chromedriver_path = '/Users/rohan/Desktop/projects/bot_env/bin/chromedriver'
            elif os.environ['DEPLOYMENT_ENVIRONMENT'] == 'PROD':
                chromedriver_path = '/var/lib/chromedriver'
            else:
                print("Development Environment not known. Check Environment variable - DEPLOYMENT_ENVIRONMENT")
                return
            driver = webdriver.Chrome(chromedriver_path, options=chrome_options)
            driver.set_window_size(800,800)
            driver.get(f'https://www.lightpollutionmap.info/#zoom=10&lat={lat}&lon={lon}&layers=B0FFFFFFTFFFFFFFFFF')
            driver.implicitly_wait(10)
            driver.find_element_by_id('CybotCookiebotDialogBodyLevelButtonLevelOptinDeclineAll').click()
            time.sleep(2)
            driver.execute_script("document.getElementById('rightMenuButton').setAttribute('style', 'display:none;')")
            driver.execute_script("document.getElementById('RightMenu').setAttribute('style', 'display:none;')")
            driver.find_element_by_id('searchBox').send_keys(f"{lat},{lon}")
            time.sleep(3)
            driver.find_element_by_class_name('ui-menu-item-wrapper').click()
            time.sleep(3)
            try:
                driver.execute_script("document.getElementById('poll_1').setAttribute('style', 'display:none;')")
            except:
                pass
            try:
                driver.execute_script("document.getElementById('adContainer_v').setAttribute('style', 'display:none;')")
            except:
                pass
            try:
                driver.execute_script("document.getElementById('adContainer_h').setAttribute('style', 'display:none;')")
            except:
                pass
            map = driver.find_element_by_id('map')
            map.screenshot('map.png')
            driver.close()
            driver.quit()
            return 1
        except:
            print(sys.exc_info())
            return 0


    def get_weather_data(self, lat, lon):
        
        openweather_url = f"https://api.openweathermap.org/data/2.5/onecall?lat={str(lat)}&lon={str(lon)}&exclude=minutely&units=metric&appid={openweather_key}"
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


    def send_current_location_weather(self, update, context):
        try:
            lat = update.message.location.latitude
            lon = update.message.location.longitude           
            try:    
                self.weather_msg, self.moon_photo = self.get_weather_data(lat, lon)
                try:
                    self.bortle_msg = self.get_bortle_info(lat, lon)
                except:
                    self.bortle_msg = ""
                if self.get_lp_img(lat, lon) == 1:
                    self.lp_img = open('map.png', 'rb')
                else:
                    self.lp_img = self.moon_photo
                update.message.reply_photo(caption = self.weather_msg, photo=self.lp_img, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='Bortle info', callback_data='bortle_info')]]))
                #context.bot.sendMessage(chat_id=update.message.chat_id, text=bortle_info)
            except:
                update.message.reply_text(text="Error in retrieving data.")
                # context.bot.sendMessage(chat_id=str(os.environ["HAC_TEST_CHAT"]), text = "AstroBot error(line 301 - current_location_weather):\n" + str(sys.exc_info()))
        except Exception as e:
            update.message.reply_text(text="Error in retrieving data.")
            # context.bot.sendMessage(chat_id=str(os.environ["HAC_TEST_CHAT"]), text = "AstroBot error(line 303 - current_location_weather):\n" + str(e))


    def send_weather_data(self, update, context):
        search_text=""
        for i in context.args:
            search_text += i + ' '
            
        if(re.search("^[0-9]",search_text)):
            lat, lon = search_text.replace(' ','').split(',')
        elif (search_text==''):
            if(update.message.chat.type == 'private'):     
                kb_list = [[KeyboardButton(text='Send Current Location', request_location=True)]]
                kb = ReplyKeyboardMarkup(kb_list, one_time_keyboard= True)
                update.message.reply_text(text="Please include a location or click the button to send current location.", reply_markup = kb)
            else:
                update.message.reply_text(text='Please include a location.')
            return
        else:
            try:
                lat, lon = self._helper.get_coordintes(search_text)
            except:
                update.message.reply_text(text='Invalid location.')
                return
                       
        try:
            og = update.message
            weather_message = og.reply_text(text = "Gathering data...")
            self.weather_msg, self.moon_photo = self.get_weather_data(lat, lon)
            self.bortle_msg = self.get_bortle_info(lat, lon)
            if self.get_lp_img(lat, lon) == 1:
                self.lp_img = open('map.png', 'rb')
            else:
                self.lp_img = self.moon_photo
            context.bot.delete_message(update.message.chat_id, weather_message.message_id)
            og.reply_photo(caption = self.weather_msg, photo=self.lp_img,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text = "Bortle Data", callback_data="bortle_info")]]))
        except:
            update.message.reply_text(text="Error in retrieving data.")
            # context.bot.sendMessage(chat_id=str(os.environ["HAC_TEST_CHAT"]), text = "AstroBot error(line 336 - get_weather):\n" + str(sys.exc_info()))


# ------------------------------------ WELCOME NEW MEMBERS -------------------------------------#

    def welcome_new_user(self, update, context):
        for new_user_obj in update.message.new_chat_members:
            new_usr = ""
            message=r"Welcome to $title, $user! Please introduce yourself and share what excites you the most about astronomy." # Welcome message
            try:
                new_usr = '@' + new_user_obj['username']
            except:
                new_usr = new_user_obj['first_name']
        welcome_message = context.bot.sendMessage(chat_id=update.message.chat_id, text = message.replace('$user',new_usr).replace('$title',update.message.chat.title))
        time.sleep(90)
        context.bot.delete_message(update.message.chat_id, welcome_message.message_id)


# ----------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------------------#

    def help(self, update, context):
        #new help
        if update.message.chat.type == 'private':
            context.bot.sendMessage(chat_id=update.message.chat_id, text= self._helper.astrobot_help)
        else:
            inline_kb = [[InlineKeyboardButton(text='AstroBot', callback_data="astrobot")],
                        [InlineKeyboardButton(text='PhotoBot', callback_data="photobot")],
                        [InlineKeyboardButton(text='BookBot', callback_data="bookbot")]]
            context.bot.sendMessage(chat_id= update.message.chat_id,text="Show commands for:", reply_markup=InlineKeyboardMarkup(inline_kb))


    def callback_query_handler(self, update, context):

        if update.callback_query.data == 'astrobot':
            update.callback_query.message.edit_text(reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="< Back", callback_data="menu")]]) ,text=self._helper.astrobot_help)
        elif update.callback_query.data == 'photobot':
            update.callback_query.message.edit_text(reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="< Back", callback_data="menu")]]) ,text=self._helper.photobot_help)
        elif update.callback_query.data == 'bookbot':
            update.callback_query.message.edit_text(reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="< Back", callback_data="menu")]]) ,text=self._helper.bookbot_help)
        elif update.callback_query.data == 'menu':
            inline_kb = [[InlineKeyboardButton(text='AstroBot', callback_data="astrobot")],
                        [InlineKeyboardButton(text='PhotoBot', callback_data="photobot")],
                        [InlineKeyboardButton(text='BookBot', callback_data="bookbot")]]
            update.callback_query.message.edit_text(reply_markup=InlineKeyboardMarkup(inline_kb), text='Show commands for:')
        elif update.callback_query.data == 'bortle_info':
            update.callback_query.message.edit_caption(reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Weather Data", callback_data="weather_info")]]) ,caption=self.bortle_msg)
        elif update.callback_query.data == 'weather_info':
            update.callback_query.message.edit_caption(reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Bortle Data", callback_data="bortle_info")]]) ,caption=self.weather_msg)


    def books_alert(self, update, context):
        if(update.message.chat.type=='private'):
            text = "Please use @LibgenLibrary_Bot to search books"
            update.message.reply_text(text)


    def hac_rules(self, update, context):
        if str(update.message.chat_id) == os.environ['HAC_CHAT']:
            rules = """1. No spam/forward from other groups.\n2. Keep the discussion in the realm of Astronomy and related sciences.\n3. NSFW content will lead to a permanent ban.\n4. Do not message members of the group privately without cause/consent.\n\nIf any rule is breached, a warning will be issued and a second breach will result in a permanent ban.\n\n\nClear skies!"""
            update.message.reply_text(text = rules)


    def creator(self, update, context):
        update.message.reply_text(text= self._helper.get_creator())