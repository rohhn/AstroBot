from bs4 import BeautifulSoup as bs4
import requests
import time
from telegram import Bot
from datetime import datetime
import pytz
import hashlib
import re

bot = Bot("1163369796:AAE1BI447fKiuDQ9RUTCUZKcS7-Ek96zlYI") #photobot
group_id ="-1001284948052"# "-1001331038106" #

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
    
def sendmessage(response):
    page_text = bs4(response.text,'html.parser')
    date = page_text.find("p").contents[3].get_text().replace("\n"," ")
    url = get_url(page_text)
    title = get_title(page_text)
    explanation = page_text.find_all('p')[2].get_text().replace("\n"," ").split("Tomorrow")[0].split("Explanation: ")[1]
    if(page_text.find('img')):
        bot.sendPhoto(chat_id=group_id, photo=url, caption = str("APOD: "+title+"\n\n"+explanation+"\nDate: " + date))
    elif(page_text.find('iframe')):
        message = ("<a href=\""+url+"\">" +"<b>Astronomy Picture of the Day</b></a>\n\n" +"\n" +explanation+"\n<i>Date: "+date+"</i>\n")
        bot.sendMessage(chat_id=group_id, text=message, parse_mode='HTML')
        

while(True):
    url = "https://apod.nasa.gov/apod/astropix.html"
    
    old_response = requests.get(url)
    old_hash = hashlib.md5(old_response.text.encode('utf-8')).hexdigest()
    
    bot.sendMessage(chat_id="1045695336", text= "Going to sleep")
    time.sleep(3600)
    
    new_response = requests.get(url)
    new_hash = hashlib.md5(new_response.text.encode('utf-8')).hexdigest()

    if(old_hash == new_hash):
        bot.sendMessage(chat_id="1045695336", text= "no change") #personal chat message
        continue
    else:
        sendmessage(new_response)
        bot.sendMessage(chat_id="-1001331038106", text= ("Updated at: " + str(datetime.now().astimezone(pytz.timezone('Asia/Kolkata')))))
        break
