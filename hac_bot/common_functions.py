import re

import requests
import telegram
from bs4 import BeautifulSoup as bs4
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackContext

from . import astrometry, utils, config

HELP_MESSAGES = [
    """Commands for the bot:\n
/weather <latitude, longitude>: Fetch current weather update for given location.\n
/weather <location name>: Fetch current weather update for given location.\n
Send map location in chat: Fetch current weather update for given location.\n
/analyze or /analyse: Plate-solve an astronomy image.\n
/find <DSO name>: Display information about any Deep Space Object present in our datastore.\n
/book <bookname>: Search for the book title on Library Genesis.\n
/help: Display all bot commands.""",
    """/start_apod: Receive daily APOD from NASA at 11AM IST.\n
/stop_apod: Stop receiving daily APOD.
/credits: Bot development credits."""
]


def get_moon_info():
    td_url = "https://www.timeanddate.com/moon/phases/india/hyderabad"
    td_response = requests.get(td_url)
    td_response = bs4(td_response.text, 'html.parser')
    moon_image = "https://www.timeanddate.com/" + str(td_response.find(id='cur-moon')['src'])
    moon_percent = td_response.find(id='cur-moon-percent').text
    moon_phase = td_response.findAll('section', {'class': 'bk-focus'})[0].find('a').text
    return moon_image, moon_percent, moon_phase


def get_weather_data(lat, lon):
    openweather_url = f"https://api.openweathermap.org/data/2.5/onecall?lat={str(lat)}&lon={str(lon)}&exclude=minutely&units=metric&appid={config.OPENWEATHER_KEY}"
    openweather_response = (requests.get(openweather_url)).json()

    cloud_cover = openweather_response['current']['clouds']
    wind_speed = round(float(openweather_response['current']['wind_speed'] * 18 / 5), 2)
    description = openweather_response['current']['weather'][0]['description']
    dew_point = openweather_response['current']['dew_point']
    temperature = openweather_response['current']['temp']
    moon_image, moon_percent, moon_phase = get_moon_info()

    weather_message = f"\nStatus: {description}\nCloud Cover: {str(cloud_cover)}%\nWind \
Speed: {str(wind_speed)}kmph\nTemperature: {str(temperature)}°C\nDew Point: {str(dew_point)}\
°C\n————————————\nMoon Illumination: {moon_percent}\nMoon Phase: {moon_phase}"
    return weather_message, moon_image


def get_bortle_info(lat, lon):
    url = "https://clearoutside.com/forecast/" + str(lat) + "/" + str(lon)
    info = []
    for i in bs4(requests.get(url).text, 'html.parser').find('span', class_='btn-primary').findAll('strong'):
        info.append(i.text)
    bortle_message_text = "Bortle " + info[1] + "\nSQM: " + info[0] + "\nArtificial Brightness: " + info[3] + "μcd/m2"
    return bortle_message_text


def remove_job(name, context):
    cur_jobs = context.job_queue.get_jobs_by_name(name)
    if not cur_jobs:
        return False
    for job in cur_jobs:
        job.schedule_removal()
    return True


def scrape(url):
    page = requests.get(url)
    page_text = bs4(page.text, 'html.parser')  # parse google news page to find all articles
    articles_text = page_text.find_all(class_="ZINbbc xpd O9g5cc uUPGi")
    return articles_text  # return list of all articles


def get_article_url(url):
    url = url.find('a').attrs['href'].replace('/url?q=', '').split('&sa')[0]
    return url


def get_time(i):
    posted_time = i.find(class_="r0bn4c rQMQod").contents[0]
    posted_time = posted_time.split(" ")
    if (posted_time[1] == 'mins' or posted_time[1] == 'min'):
        time_since = int(posted_time[0])
    if (posted_time[1] == 'hours' or posted_time[1] == 'hour'):
        time_since = 60 * int(posted_time[0])
    elif (posted_time[1] == 'days' or posted_time[1] == 'day'):
        time_since = 24 * 60 * int(posted_time[0])
    elif (posted_time[1] == 'weeks' or posted_time[1] == 'week'):
        time_since = 7 * 24 * 60 * int(posted_time[0])
    else:
        time_since = 9999999
    return (time_since)  # return time since posted


def get_coordintes(search_text):
    geolocation_url = "https://dev.virtualearth.net/REST/v1/Locations?key=" + config.VIRTUALEARTH_KEY + "&o=json&q=" + search_text + "&jsonso=" + search_text
    geolocation_response = (requests.get(geolocation_url)).json()
    lat = round(geolocation_response['resourceSets'][0]['resources'][0]['point']['coordinates'][0], 2)
    lon = round(geolocation_response['resourceSets'][0]['resources'][0]['point']['coordinates'][1], 2)
    return lat, lon


async def bot_credits(update: Update, context: CallbackContext):
    if all((utils.is_not_blacklist(update), utils.is_approved(update))):
        message = "This bot has been created by @cosmicpasta, @skilledspark and @dewwakakkar."
        await update.message.reply_text(text=message)


async def bot_help(update: Update, context: CallbackContext):

    # message = "Commands for @HAC_AstroBot:\n\n/randomarticle - Fetch a random article related to an astronomy subject.\n\n/wiki <keyword> - Generate a short summary and link to wikipedia.\n\n/weather <latitude, longitude> or\n/weather <location name> or\nsending a map location - Fetch a weather update.\n\n/news <search phrase> - search for related articles on Google News.\n\n/analyze or /analyse - Plate-solve an astronomy image.\n\n/find <DSO name> - Display information about any Deep Space Object present in our datastore.\n\n/book <bookname> - Search for the book title on Library Genesis.\n\n/help - Display all bot commands."

    if all((utils.is_not_blacklist(update), utils.is_approved(update))):
        markup = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(text="More commands", callback_data="bot_helper_more")
            ]]
        )
        await update.message.reply_text(text=HELP_MESSAGES[0], reply_markup=markup)


def get_astrometry_detailed_message(identified_objects):
    detailed_msg = ""
    for obj in identified_objects:
        if re.search('^M ', obj):
            obj = re.sub("M ", "Messier ", obj)

        obj_search_index = obj.replace(' ', '').lower()

        if obj_search_index in config.DSO_DATA:
            detailed_msg += config.DSO_DATA[obj_search_index]['short_description'] + "\n\n"

    return detailed_msg


def get_astrometry_identified_objects(job_id):
    job_info = astrometry.get_job_info(job_id)
    return job_info['objects_in_field']


def callback_query_handler(update: Update, context: CallbackContext):
    if update.callback_query.data.startswith('bortle_'):
        lat, lon = update.callback_query.data.replace('bortle_', '').split('_')
        update.callback_query.message.edit_caption(reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Weather Data", callback_data="weather_{}_{}".format(lat, lon))]]),
                                                   caption=get_bortle_info(lat, lon))

    elif update.callback_query.data.startswith('weather_'):
        lat, lon = update.callback_query.data.replace('weather_', '').split('_')
        weather_message, _ = get_weather_data(lat, lon)
        update.callback_query.message.edit_caption(reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Bortle Data", callback_data="bortle_{}_{}".format(lat, lon))]]),
                                                   caption=weather_message)

    elif update.callback_query.data.startswith('list_astrometry_objects_'):

        jobid = update.callback_query.data.split('list_astrometry_objects_')[1]
        identified_objects = "Identified objects: {}".format(', '.join(get_astrometry_identified_objects(jobid)))
        update.callback_query.message.edit_caption(
            reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton(text="< Back", callback_data="back_astrometry_{}".format(jobid))
                ]]
            ),
            caption=identified_objects
        )

    elif update.callback_query.data.startswith('detailed_astrometry_objects_'):

        jobid = update.callback_query.data.split('detailed_astrometry_objects_')[1]
        detailed_msg = get_astrometry_detailed_message(get_astrometry_identified_objects(jobid))
        try:
            update.callback_query.message.edit_caption(
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="< Back", callback_data="back_astrometry_{}".format(jobid))]]
                ),
                caption=detailed_msg
            )
        except telegram.error.BadRequest as error:
            if str(error) == 'Media_caption_too_long':
                update.callback_query.message.reply_text(text=detailed_msg)

    elif update.callback_query.data.startswith('back_astrometry_'):
        jobid = update.callback_query.data.split('back_astrometry_')[1]
        update.callback_query.message.edit_caption(
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(text="List identified objects",
                                          callback_data="list_astrometry_objects_{}".format(jobid))],
                    [InlineKeyboardButton(text="Detailed objects info",
                                          callback_data="detailed_astrometry_objects_{}".format(jobid))]
                ]
            ),
            caption=""
        )

    elif update.callback_query.data.startswith('full_dso_data_'):
        object_search_index = update.callback_query.data.split('full_dso_data_')[1]
        found_object = config.DSO_DATA[object_search_index]

        try:
            update.callback_query.message.edit_caption(reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="< Back", callback_data="back_dso_data_{}".format(object_search_index))]]),
                                                       caption=found_object['full_description'])
        except telegram.error.BadRequest as error:
            if str(error) == 'Media_caption_too_long':
                update.callback_query.message.edit_reply_markup(reply_markup=None)
                update.callback_query.message.reply_text(text=found_object['full_description'])

    elif update.callback_query.data.startswith('back_dso_data_'):
        object_search_index = update.callback_query.data.split('back_dso_data_')[1]
        found_object = config.DSO_DATA[object_search_index]
        update.callback_query.message.edit_caption(reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
            text="Get detailed information", callback_data="full_dso_data_".format(object_search_index))]]),
                                                   caption=found_object['short_description'])

    elif update.callback_query.data == 'bot_helper_more':

        markup = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(text="< Back", callback_data="bot_helper_back")
            ]]
        )
        update.callback_query.message.edit_text(text=HELP_MESSAGES[1], reply_markup=markup)

    elif update.callback_query.data == 'bot_helper_back':

        markup = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(text="More commands", callback_data="bot_helper_more")
            ]]
        )
        update.callback_query.message.edit_text(text=HELP_MESSAGES[0], reply_markup=markup)


async def testing(update: Update, context: CallbackContext):
    await update.message.reply_text(text=str(update.message.from_user.id))
    await update.message.reply_text(text=str(update.message.chat_id))
