from bs4 import BeautifulSoup as bs4
from telegram.ext import Updater
import requests
from better_profanity import profanity
import smtplib
import time

while(True):
    url = "https://apod.nasa.gov/apod/astropix.html"
    response = requests.get(url)
    page_text = bs4(response.text, 'html.parser')
    
    date = page_text.find("p").contents[3].get_text().replace('\n','')
    image_url = "https://apod.nasa.gov/apod/"+page_text.find_all('center')[0].find('img')['src']
    title = page_text.find_all('center')[1].get_text().replace("\n","")
    

    if(date == page_text.find("p").contents[3].get_text().replace('\n','')):
        print("sleeping")
        time.sleep(60)
        print("awake")
        continue
    else:
        msg = "updated"
        toad = ['deshmukh.rohan06@gmail.com', 'singh.s.lakshya@gmail.com']
        fromad = 'deshmukhr849@gmail.com'
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('deshmukhr849@gmail.com','dabaredyh')
        
        server.sendmail(fromad, toad, msg)
        server.quit()
        print("mail sent")
        
        break
        
#def main():
#    #day = datetime.datetime.now().strftime("%A")
#    #time = int(datetime.datetime.now().strftime("%H"))
#    
#    updater = Updater('1183471904:AAENQORzTAU_mTDXfv8xJU1s3rmK1PuzlpU')
#    dp = updater.dispatcher
#    dp.add_handler(CommandHandler('wiki',get_wiki_info))
#    #dp.add_handler(MessageHandler(~Filters.command & Filters.text, test))
#    updater.start_polling()
#    updater.idle()
#
#if __name__ == '__main__':
#    main()
#