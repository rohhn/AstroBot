import os
import sys
import random
import time
import pytz
import datetime
import traceback
import re
from io import BytesIO
import requests
from bs4 import BeautifulSoup as bs4
from telegram.ext import CallbackContext
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, Update
from better_profanity import profanity
from . import common_functions, utils, config
from selenium import webdriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')

ind_tz = pytz.timezone('Asia/Kolkata')

if config.GOOGLE_CHROME_BIN is not None:
    chrome_options.binary_location = config.GOOGLE_CHROME_BIN


class AstroBot:

# ------------------- GENERATE RANDOM ARTICLES FROM POOL OF TOPICS ----------------------#

    def get_random_article(self):

        random_topics=['astronomy', 'latest+astronomy+news', 'astronomy+events','black+holes', 'space+exploration', 'hubble+space+telescope','space+observatory','astrophysics', 'Cosmology', 'Astrophotography'] #Topics for random article generator

        keyword = random_topics[random.randint(0,len(random_topics)-1)]
        url = "https://www.google.com/search?q="+keyword+"&source=lnms&tbm=nws&sa=X&ved=2ahUKEwjTi4TOw_7qAhWzyDgGHVjpAyYQ_AUoAXoECBUQAw&biw=1680&bih=948"
        articles_text = common_functions.scrape(url)
        data = []
        for i in articles_text:
            data.append([common_functions.get_article_url(i),common_functions.get_time(i),i.find(class_ = "BNeawe vvjwJb AP7Wnd").contents[0]])

        return(data[random.randrange(0,len(articles_text),1)][0])

    
    # /randomarticle
    @utils.is_not_blacklist
    @utils.is_approved
    def send_random_article(self, update: Update, context: CallbackContext):
        try:
            update.message.reply_text(self.get_random_article())
        except:
            update.message.reply_text("Error in retrieving data.")

# ----------------------------------- DAILY ARTICLES -------------------------------------- #
    
    # @utils.is_not_blacklist
    # @utils.is_approved
    def get_daily_article(self, context):
        weekly_article_topics=['astronomy', 'latest+astronomy+news', 'astronomy+events','space+observations']
        day = datetime.datetime.now().astimezone(ind_tz).strftime("%A")
        if day == 'Friday':
            topic_day = 'the+sky+this+week+site:astronomy.com'  #Astronomy magazine weekly update
        else:
            topic_day = weekly_article_topics[random.randint(0,len(weekly_article_topics)-1)] #Random article from pool of topics
        
        url = "https://www.google.com/search?q="+topic_day+"&source=lnms&tbm=nws&sa=X&ved=2ahUKEwjZzKWTjv3qAhVFyzgGHeKzCf8Q_AUoAXoECBUQAw&biw=1680&bih=947"

        data = []
        for i in common_functions.scrape(url):
            data.append([common_functions.get_article_url(i),common_functions.get_time(i),i.find(class_ = "BNeawe vvjwJb AP7Wnd").contents[0]])
        data = sorted(data, key = lambda x:x[1])
        context.bot.sendMessage(chat_id = context.job.context,text = (data[0][0]))


    # /daily_articles
    @utils.is_not_blacklist
    @utils.is_approved
    def send_daily_article(self, update,context):
        job_removed= common_functions.remove_job(str(update.message.chat_id), context)
        if(job_removed):
            r = context.bot.sendMessage(chat_id=update.message.chat_id, text="Running instance terminated.")
            context.bot.delete_message(update.message.chat_id, r.message_id)
            
        context.bot.sendMessage(chat_id = update.message.chat_id, text="Articles related to astronomy will be everyday.\n\n Clear Skies!")
        context.job_queue.run_daily(self.get_daily_article, time = datetime.time(17,0,0,tzinfo=ind_tz), context = update.message.chat_id, name=str(update.message.chat_id))
  

    # /stop_daily_articles
    @utils.is_not_blacklist
    @utils.is_approved
    def stop_daily_article(self, update: Update, context: CallbackContext):
        job_removed = common_functions.remove_job(str(update.message.chat_id), context)
        if(job_removed):
            context.bot.sendMessage(chat_id=update.message.chat_id, text='Daily articles have been stopped.')

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
                for i in common_functions.scrape(url):
                    data.append([common_functions.get_article_url(i),common_functions.get_time(i),i.find(class_ = "BNeawe vvjwJb AP7Wnd").contents[0]])
                return(data)
            except:
                return False

    @utils.is_not_blacklist
    @utils.is_approved
    def send_inline_news(self, update: Update, context: CallbackContext):
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
    @utils.is_not_blacklist
    @utils.is_approved
    def send_news_article(self, update: Update, context: CallbackContext):
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

    @utils.is_not_blacklist
    @utils.is_approved
    def send_wiki_info(self, update: Update, context: CallbackContext):
        search_text = update.message.text.split('/wiki')[1].strip()
        search_text += "+site:wikipedia.org"
        update.message.reply_text(self.get_wiki_summary(search_text.lower()))

# ------------------------------------ WEATHER UPDATES --------------------------------------#

    def get_lp_img(self, lat, lon):

        img_file = None

        try:
            driver = webdriver.Chrome(config.CHROMEDRIVER_PATH, options=chrome_options)
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
            temp_img = map.screenshot_as_png
            img_file = BytesIO(temp_img)
        except:
            print(sys.exc_info())
        finally:
            driver.close()
            driver.quit()

        return img_file

    @utils.is_not_blacklist
    @utils.is_approved
    def send_current_location_weather(self, update: Update, context: CallbackContext):
        try:
            lat = update.message.location.latitude
            lon = update.message.location.longitude           
            try:    
                weather_msg, moon_photo = common_functions.get_weather_data(lat, lon)
                lp_img = self.get_lp_img(lat, lon)
                if lp_img is None:
                    lp_img = moon_photo
                update.message.reply_photo(caption = weather_msg, photo=lp_img, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='Bortle info', callback_data='bortle_{}_{}'.format(lat, lon))]]))
            except:
                update.message.reply_text(text="Error in retrieving data.")
        except Exception as e:
            update.message.reply_text(text="Error in retrieving data.")

    @utils.is_not_blacklist
    @utils.is_approved
    def send_weather_data(self, update: Update, context: CallbackContext):

        search_text = update.message.text.split('/weather')[1].strip()
            
        if(re.search("^[0-9]",search_text)):
            lat, lon = search_text.replace(' ','').split(',')
        elif (search_text==''):
            if(update.message.chat.type == 'private'):     
                kb_list = [[KeyboardButton(text='Send Current Location', request_location=True)]]
                kb = ReplyKeyboardMarkup(kb_list, one_time_keyboard= True)
                update.message.reply_text(text="Include a location or click the button to send current location.", reply_markup = kb)
            else:
                update.message.reply_text(text='Include a location to search.')
            return
        else:
            try:
                lat, lon = common_functions.get_coordintes(search_text)
            except:
                update.message.reply_text(text='Invalid location.')
                return
                       
        try:
            og = update.message
            weather_message = og.reply_text(text = "Gathering data...")
            weather_msg, moon_photo = common_functions.get_weather_data(lat, lon)
            lp_img = self.get_lp_img(lat, lon)
            if lp_img is None:
                lp_img = moon_photo
            context.bot.delete_message(update.message.chat_id, weather_message.message_id)
            og.reply_photo(caption = weather_msg, photo=lp_img,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text = "Bortle Data", callback_data="bortle_{}_{}".format(lat, lon))]]))
        except:
            print(traceback.format_exc())
            update.message.reply_text(text="Error in retrieving data.")

# ------------------------------------ WELCOME NEW MEMBERS -------------------------------------#

    @utils.is_approved
    def welcome_new_user(self, update: Update, context: CallbackContext):
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

    def hac_rules(self, update: Update, context: CallbackContext):
        if str(update.message.chat_id) == os.environ['HAC_CHAT']:
            rules = """1. No spam/forward from other groups.\n2. Keep the discussion in the realm of Astronomy and related sciences.\n3. NSFW content will lead to a permanent ban.\n4. Do not message members of the group privately without cause/consent.\n\nIf any rule is breached, a warning will be issued and a second breach will result in a permanent ban.\n\n\nClear skies!"""
            update.message.reply_text(text = rules)
