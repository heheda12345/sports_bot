import configparser
import telebot
import time
import urllib
import xingzhe
import strava
import convert
import datetime
import xml.etree.ElementTree as ET
import os

config = configparser.ConfigParser()
config.read("config.ini")

BOT_TOKEN = config['telegram']['bot_token']
bot = telebot.TeleBot(BOT_TOKEN)

help_msg = "hello world"

last_gpx_file = None
if not os.path.exists('./gpx'):
    os.makedirs('./gpx')

@bot.message_handler(content_types=['document'])
def handle_file(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        file_extension = message.document.file_name.split('.')[-1].lower()

        if file_extension == 'gpx':
            file_url = f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}'
            file_name = message.document.file_name
            file_path = f'./gpx/{file_name}'
            urllib.request.urlretrieve(file_url, file_path)
            global last_gpx_file
            last_gpx_file = file_path
            bot.reply_to(message, f"File '{file_name}' has been saved locally.")
        else:
            bot.reply_to(message, f"File extension '{file_extension}' is not supported.")
    except Exception as e:
        bot.reply_to(message, f"An error occurred while processing the file: {e}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, help_msg)

@bot.message_handler(commands=['uploadXingzhe'])
def upload_xingzhe(message):
    if message.text != '/uploadXingzhe':
        title = message.text.split(' ', 1)[1]
    else:
        title = None
    title_app, file_path = xingzhe.download_latest()
    if title is None: title = title_app
    msg = strava.post_activity(file_path, title)
    bot.reply_to(message, msg)



@bot.message_handler(commands=['uploadZeep'])
def upload_zeep(message):
    if message.text != '/uploadZeep':
        title = message.text.split(' ', 1)[1]
    else:
        title = None
    if last_gpx_file is None:
        bot.reply_to(message, "No GPX file found.")
        return
    def readable_title(date_string):
        # something like 20230531214756
        print("date_string", date_string)
        year = date_string[:4]
        month = date_string[4:6]
        day = date_string[6:8]
        hour = date_string[8:10]
        minute = date_string[10:12]
        second = date_string[12:14]
        date_format = "%Y%m%d%H%M%S"
        title = f"{year}.{month}.{day} {hour}:{minute}:{second}"
        return title

    converted_gpx_file = last_gpx_file.replace('.gpx', '_wgs.gpx')
    convert.convert(last_gpx_file, converted_gpx_file)
    try:
        activity_type = convert.get_activity_type(last_gpx_file)
    except Exception as e:
        bot.reply_to(message, f"An error occurred while getting the sport type: {e}")
        return
    if title is None: title = activity_type + " " + readable_title(last_gpx_file.split('/')[-1][8:22])
    msg = strava.post_activity(converted_gpx_file, title, activity_type=activity_type)
    print("msg", type(msg), msg)
    bot.reply_to(message, msg)

bot.polling()