from bs4 import BeautifulSoup as bs4
from telegram.ext import CommandHandler, Updater
import requests
from better_profanity import profanity

def get_wiki_link(search_text):
    google_url = "https://www.google.com/search?q="+search_text+"&rlz=1C5CHFA_enIN908IN908&oq="+search_text+"&aqs=chrome.0.69i59.6224j0j1&sourceid=chrome&ie=UTF-8"
    google_page = requests.get(google_url)
    google_page = bs4(google_page.text,'html.parser')
    google_page = google_page.find(class_ = "ZINbbc xpd O9g5cc uUPGi")
    wiki_link = google_page.find('a')['href'].replace('/url?q=','')
    wiki_link = wiki_link.split("&sa")[0]
    return(wiki_link)

def scrape_wiki(search_text):
    if(profanity.contains_profanity(search_text)):
        return("BAZINGA!")
    else:
        wiki_link = get_wiki_link(search_text)
        wiki_page = requests.get(wiki_link)
        wiki_page = bs4(wiki_page.text,'html.parser')
        summary = wiki_page.find_all('p')[1].get_text()
        image_url = "https://en.wikipedia.org"+ wiki_page.find('table').find('a')['href']
        text = summary + "\n\n" + wiki_link
        return(text)

def get_wiki_info(update, context):
    chat_id = update.message.chat_id
    search_text=""
    for i in context.args:
        search_text = search_text + " " +i
    search_text = search_text + "+wiki"
    update.message.reply_text(scrape_wiki(search_text))

def main():
    #day = datetime.datetime.now().strftime("%A")
    #time = int(datetime.datetime.now().strftime("%H"))
    
    updater = Updater('1183471904:AAENQORzTAU_mTDXfv8xJU1s3rmK1PuzlpU', use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('wiki',get_wiki_info))
    #dp.add_handler(MessageHandler(~Filters.command & Filters.text, test))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
