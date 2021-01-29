from bs4 import BeautifulSoup as bs4
import requests
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
import datetime
import random
import re
from better_profanity import profanity
import pytz
import time
import sys
from libgen_api import LibgenSearch
ls = LibgenSearch()
from hac_bot.astrobot import Helper

class BookBot():
	def __init__(self):
		self.h = Helper()
		return

	def get_book_download_link(self,url):
		page = bs4((requests.get(url)).text, 'html.parser')
		link = page.find('div', id='download').findAll('a')[1].attrs['href']
		alt_link = page.find('div', id='download').findAll('a')[0].attrs['href']
		return link, alt_link

	def get_book_cover_img(self, url):
		page = bs4((requests.get(url)).text, 'html.parser')
		img_url = 'http://library.lol/' + page.find('img').attrs['src']
		return img_url

	'''INLINE FEATURE FOR BOOKS'''

	def send_book(self, update, context):
		query = update.inline_query.query
		params = query.split(' by ')
		try:
			filters = {'Extension':'pdf'}
			results = list()
			if not query:
				return
			books = ls.search_title_filtered(params[0].strip(), filters)
			max_results = len(books) if len(books) < 5 else 5
			if books:
				for i in range(max_results):
					results.append(
						InlineQueryResultArticle(
							id = books[i]['ID'],
							title = books[i]['Title'] + ' by ' + books[i]['Author'],
							input_message_content = InputTextMessageContent(message_text = '<a href=\''+self.get_book_download_link(books[i]['Mirror_1'])[0] + '\'>'+books[i]['Title'] + ' by ' + books[i]['Author']+'</a>', parse_mode= 'HTML')
							#url = self.get_book_cover_img(books[i]['Mirror_1'])
						)
					)
			else:
				results.append(
					InlineQueryResultArticle(
						id="0",
						title='No results found',
						input_message_content= InputTextMessageContent(message_text='<a href=\'http://libgen.rs\'>Libgen Library</a>', parse_mode='HTML', disable_web_page_preview=True)))
			context.bot.answer_inline_query(update.inline_query.id, results)
			context.bot.delete_message(chat_id=self.x.chat.id, message_id = self.x.message_id)
		except:
			print(str(sys.exc_info()))

	def new_books(self, update, context):
		search_text = ''
		for i in context.args:
			search_text += i + ' '
		try:
			kb_list = [[InlineKeyboardButton(text='Search', switch_inline_query_current_chat=search_text.strip())]]
			kb = InlineKeyboardMarkup(kb_list)
			update.message.reply_text(text=search_text, reply_markup = kb)
		except:
			kb_list = [[InlineKeyboardButton(text='Search', switch_inline_query_current_chat="")]]
			kb = InlineKeyboardMarkup(kb_list)
			self.x = update.message.reply_text(text='Click the button to search', reply_markup = kb)

	def help(self, update, context):
		if update.message.chat.type == 'private':
			context.bot.sendMessage(chat_id=update.message.chat_id, text=self.h.bookbot_help)