import configparser
import telebot
import time
import urllib
import xingzhe
import strava
config = configparser.ConfigParser()
config.read("config.ini")

BOT_TOKEN = config['telegram']['bot_token']
bot = telebot.TeleBot(BOT_TOKEN, parse_mode='markdown')

help_msg = "hello world"

last_gpx_file = None

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
    print("message", message)
    print(message.text)
    if message.text != '/uploadXingzhe':
        title = message.text.split(' ', 1)[1]
    else:
        title = None
    title_app, file_path = xingzhe.download_latest()
    if title is None: title = title_app
    msg = strava.post_activity(file_path, title)
    bot.reply_to(message, msg)


bot.polling()