from bs4 import BeautifulSoup as bs4
from telegram.ext import Updater
import requests
from better_profanity import profanity

while(True):
    url = "https://apod.nasa.gov/apod/astropix.html"
    response = requests.get(url)
    page_text = bs4(response.text, 'html.parser')
    
    date = page_text.find("p").contents[3].get_text().replace('\n','')
    image_url = "https://apod.nasa.gov/apod/"+page_text.find_all('center')[0].find('img')['src']
    title = page_text.find_all('center')[1].get_text().replace("\n","")
    

    if(date == page_text.find("p").contents[3].get_text().replace('\n','')):
        time.sleep(86000)
        continue
    else:
        updater = Updater('1183471904:AAENQORzTAU_mTDXfv8xJU1s3rmK1PuzlpU')
        dp.updater.dispatcher
        
def main():
    #day = datetime.datetime.now().strftime("%A")
    #time = int(datetime.datetime.now().strftime("%H"))
    
    updater = Updater('1183471904:AAENQORzTAU_mTDXfv8xJU1s3rmK1PuzlpU')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('wiki',get_wiki_info))
    #dp.add_handler(MessageHandler(~Filters.command & Filters.text, test))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
