import logging
import telebot
from typing import Final
from environs import Env
from persistent import Storage

logging.basicConfig(encoding='utf-8', level=logging.INFO)

env = Env()
env.read_env()

TOKEN: Final[str] = env.str('API_TOKEN')

logging.info(TOKEN)

storage = Storage()

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    storage.add("Feiteira", 2, "16")
    bot.reply_to(message, "Sup Bich?")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, message.text)

bot.infinity_polling()