from bs4 import BeautifulSoup as bs4
from telegram.ext import Updater
import requests
from better_profanity import profanity
import smtplib
import time
import hashlib
from urllib.request import urlopen

while(True):
    url = "https://www.youtube.com"
    #response = urlopen(url).read()
    
    #page_text = bs4(response.text, 'html.parser')
    
    try:
        old_response = requests.get(url)
        old_page_text = bs4(old_response.text, 'html.parser')
        old_hash = hashlib.sha224(str(old_page_text)).hexdigest()
        #old_date = old_page_text.find("p").contents[3].get_text().replace('\n','')
        #old_image_url = "https://apod.nasa.gov/apod/"+old_page_text.find_all('center')[0].find('img')['src']
        #old_title = old_page_text.find_all('center')[1].get_text().replace("\n","")
    
        print(time.time())
        time.sleep(60)
        
        #response = urlopen(url).read()
        #new_hash = hashlib.sha224(response).hexdigest()
        
        
        new_response = requests.get(url)
        new_page_text = bs4(new_response.text, 'html.parser')
        new_hash = hashlib.sha224(str(new_page_text)).hexdigest()
        #new_date = new_page_text.find("p").contents[3].get_text().replace('\n','')
        #new_image_url = "https://apod.nasa.gov/apod/"+new_page_text.find_all('center')[0].find('img')['src']
        #new_title = new_page_text.find_all('center')[1].get_text().replace("\n","")
    

        if(old_hash == new_hash):
            print("no change")
            continue
        else:
            
            #new_date = page_text.find("p").contents[3].get_text().replace('\n','')
            #new_image_url = "https://apod.nasa.gov/apod/"+page_text.find_all('center')[0].find('img')['src']
            #new_title = page_text.find_all('center')[1].get_text().replace("\n","")
            msg = "apod updated"
            #toad = ['deshmukh.rohan06@gmail.com', 'singh.s.lakshya@gmail.com']
            TOAD = 'deshmukh.rohan06@gmail.com'
            fromad = 'deshmukhr849@gmail.com'
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login('deshmukhr849@gmail.com','dabaredyh')
            
            server.sendmail(fromad, toad, msg)
            server.quit()
            print("mail sent")
            
            old_response = requests.get(url)
            old_page_text = bs4(old_response.text, 'html.parser')
            old_hash = hashlib.sha224(str(old_page_text)).hexdigest()
            time.sleep(60)
            
            continue
    except Exception as e:
        msg = "apod updated"
        toad = 'deshmukh.rohan06@gmail.com'
        fromad = 'deshmukhr849@gmail.com'
            
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('deshmukhr849@gmail.com','dabaredyh')
        
        server.sendmail(fromad, toad, msg)
        server.quit()
        print("mail sent")
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