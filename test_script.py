from telegram import Bot, Update
from datetime import datetime
import pytz
from datetime import timezone

#time.astimezone(pytz.timezone('Asia/Kolkata')).strftime("%H")

bot = Bot("1222703294:AAEnBuUwV4H8GSv-h2e3Jgfv77QMqpTRsVc")
msg="time now: " + str(datetime.now().astimezone(pytz.timezone('Asia/Kolkata')))
bot.sendMessage(chat_id="-1001331038106",text=msg)