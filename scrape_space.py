#!/usr/bin/env python
# coding: utf-8

# In[32]:


import pandas as pd
from bs4 import BeautifulSoup as bs4
import requests
import json

url = input("Enter URL:")

# In[83]:

def scrape_page(url):
    page  = requests.get(url)
    page_text = bs4(page.text,'html.parser')

    articles = page_text.find_all(class_ = 'article-link')
    columns=['page_url','date_posted','article_name','article_url','article_image_url','summary']
    data = []
    for i in articles:
        data.append([url, i.find('time').attrs['datetime'], i.find(class_ = 'article-name').contents[0], i.attrs['href'], i.find('source').attrs['data-original-mos'], i.find(class_ = 'synopsis').contents[0]])
    df = pd.DataFrame(data, columns=columns)
    





# In[84]:




# In[90]:





# In[82]:


print(df.shape)
print(df['article_name'])


# In[ ]:




