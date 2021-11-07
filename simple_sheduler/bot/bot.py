import logging
import os
import telebot
from typing import Final
from persistent import Storage
from environs import Env

env = Env()
env.read_env()

logging.basicConfig(level=logging.INFO)

TOKEN: Final[str] = env('API_TOKEN')

logging.info(TOKEN)

storage = Storage()

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['reserva'])
def reservation(message):
    name: str = f"{message.from_user.first_name} {message.from_user.last_name}"
    content: str = message.text.split()
    logging.info(content)
    if len(content) <=1 :
        bot.reply_to(message, "Reserva inválida. Falta número de slots e/ou horas")
    else:
        msg = storage.add(name, content[1])
        bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['cancelar'])
def cancel(message):
    name: str = f"{message.from_user.first_name} {message.from_user.last_name}"
    msg: str = storage.remove(name)
    bot.reply_to(message, msg)

@bot.message_handler(commands=['lista'])
def list(message):
    msg: str = storage.list()
    bot.reply_to(message, msg)

@bot.message_handler(commands=['ajuda'])
def help(message):
    bot.reply_to(message, "\n/reserva [hora] -> reserva a aula às [hora] horas\n/cancelar -> cancela a aula marcada previamente\n/lista -> lista as marcações do dia\n")

bot.infinity_polling()