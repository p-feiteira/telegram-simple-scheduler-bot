import logging
import os
from typing import Final, List

import telebot
from environs import Env
from persistent import Storage

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
    content: List[str] = message.text.split()
    logging.info(content)
    if len(content) <=1 :
        bot.reply_to(message, "Reserva inválida. Falta horas")
    else:
        if "hoje" in content:
            msg = storage.add(name=name, today=True, hour=content[2])
        else:
            msg = storage.add(name=name, hour=content[1])
            
        bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['cancelar'])
def cancel(message):
    name: str = f"{message.from_user.first_name} {message.from_user.last_name}"
    if "hoje" in message.text:
        msg: str = storage.remove(name=name, today=True)
    else:
        msg: str = storage.remove(name=name)
    bot.reply_to(message, msg)

@bot.message_handler(commands=['lista'])
def list(message):
    msg: str = storage.list()
    bot.reply_to(message, msg)

@bot.message_handler(commands=['ajuda'])
def help(message):
    bot.reply_to(message, "\n/reserva [hoje] [hora] -> reserva a aula para amanhã/hoje às [hora] horas\n/cancelar -> cancela a aula marcada previamente\n/lista -> lista as marcações do dia\n")

bot.infinity_polling()