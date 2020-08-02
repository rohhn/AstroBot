#!/usr/bin/env python
# coding: utf-8

# In[114]:


import pandas as pd
from bs4 import BeautifulSoup as bs4
import requests
import json


# In[172]:


def scrape(url):
    page  = requests.get(url)
    page_text = bs4(page.text,'html.parser')
    articles_text = page_text.find_all(class_ = "ZINbbc xpd O9g5cc uUPGi")
    return articles_text


# In[173]:


def get_url(i):
    i = i.find('a').attrs['href'].replace('/url?q=','')
    return i


# In[174]:


def get_time(i):
    posted_time = i.find(class_ = "r0bn4c rQMQod").contents[0]
    posted_time = posted_time.split(" ")
    if (posted_time[1] == 'hours' or posted_time[1] == 'hour'):
        time_since = 0.1 * int(posted_time[0])
    elif (posted_time[1] == 'days' or posted_time[1] == 'day'):
        time_since = 1 * int(posted_time[0])
    else:
        time_since = 999
    return(time_since)


# In[175]:


def get_final_article(articles_text):
    data = []
    for i in articles_text: 
        data.append([get_url(i),get_time(i),i.find(class_ = "BNeawe vvjwJb AP7Wnd").contents[0]])
    data = sorted(data, key = lambda x: x[1])
    return(data[0][0])


# In[176]:


def get_article():
    keyword = input("Search query:")
    url = "https://www.google.com/search?q="+keyword+"&source=lnms&tbm=nws&sa=X&ved=2ahUKEwjZzKWTjv3qAhVFyzgGHeKzCf8Q_AUoAXoECBUQAw&biw=1680&bih=947"
    articles_text = scrape(url)
    return(get_final_article(articles_text))


# In[177]:


x = get_article()
print(x)


# In[ ]:




