import logging
import os
import telebot
from typing import Final
from persistent import Storage

logging.basicConfig(level=logging.INFO)

TOKEN: Final[str] = os.getenv('API_TOKEN')

logging.info(TOKEN)

storage = Storage()

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['reserva'])
def send_welcome(message):
    name: str = f"{message.from_user.first_name} {message.from_user.last_name}"
    content: str = message.text.split()
    logging.info(content)
    if len(content) <=1 :
        bot.reply_to(message, "Reserva inválida. Falta número de slots e/ou horas")
    else:
        storage.add(name, int(content[1]), content[2])
        bot.reply_to(message, f"{name} reserva para {content[1]} pessoa(s) às {content[2]} dia 0/0/0000 registada com sucesso.")

@bot.message_handler(commands=['cancelar'])
def cancel(message):
    name: str = f"{message.from_user.first_name} {message.from_user.last_name}"
    storage.remove(name)
    bot.reply_to(message, message.text)

bot.infinity_polling()