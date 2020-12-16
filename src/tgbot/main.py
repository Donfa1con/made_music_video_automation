# -*- coding: utf-8 -*-

import glob
import json
import os
import time

import telebot
from telebot import types

from common.config import RABBIT_CONFIG, VIDEO_FORMATS, IMAGE_FORMATS, AUDIO_FORMATS, DEFAULT_SETTINGS, USER_CONFIG_NAME
from common.rabbit_worker import RabbitMQWorker

BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise Exception("BOT_TOKEN is undefined")
BOT = telebot.TeleBot(BOT_TOKEN)


def get_last_folder_by_id(user_id):
    user_data_path = os.path.join(os.environ.get('USER_DATA'), user_id)
    all_folders = filter(lambda x: '.json' not in x, glob.glob(f'{user_data_path}/*'))
    if all_folders:
        return max(all_folders, key=lambda x: int(x.split('/')[-1]))


def init_new_folder(user_id):
    user_data_path = os.path.join(os.environ.get('USER_DATA'), user_id)
    new_folder_name = os.path.join(user_data_path, str(int(time.time())))
    os.makedirs(os.path.join(new_folder_name, 'videos'))
    os.makedirs(os.path.join(new_folder_name, 'images'))
    os.makedirs(os.path.join(new_folder_name, 'audios'))


def get_folder_by_ext(path):
    ext = os.path.splitext(os.path.basename(path))[1]
    if ext in VIDEO_FORMATS:
        return 'videos'
    if ext in IMAGE_FORMATS:
        return 'images'
    if ext in AUDIO_FORMATS:
        return 'audios'


def save_settings(user_id, settings=DEFAULT_SETTINGS):
    user_data_path = os.path.join(os.environ.get('USER_DATA'), str(user_id), USER_CONFIG_NAME)
    with open(user_data_path, 'w') as f:
        json.dump(settings, f)


def load_settings(user_id):
    user_data_path = os.path.join(os.environ.get('USER_DATA'), str(user_id), 'settings.json')
    if not os.path.exists(user_data_path):
        save_settings(user_id)
    with open(user_data_path, 'r') as f:
        return json.load(f)


def build_main_menu(user_id):
    keyboard = telebot.types.ReplyKeyboardMarkup()
    keyboard.row('/create')
    keyboard.row('/settings')
    keyboard.row('/demo')
    BOT.send_message(user_id, "Let's create", reply_markup=keyboard)
    return keyboard


def build_settings_menu(user_id, text="Enable/Disable stages"):
    settings = load_settings(user_id)
    keyboard = telebot.types.ReplyKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton(f'Quality - {settings["stages"]["quality"]}',
                                            callback_data='quality'),
                 types.InlineKeyboardButton(f'Highlights - {settings["stages"]["highlights"]}',
                                            callback_data='highlights'))
    keyboard.row(types.InlineKeyboardButton(f'Music recommendation - {settings["stages"]["music_recommendation"]}',
                                            callback_data='music_recommendation'),
                 types.InlineKeyboardButton(f'Visbeat - {settings["stages"]["visbeat"]}',
                                            callback_data='visbeat'))
    keyboard.row(types.InlineKeyboardButton('Main menu', callback_data='menu'))
    BOT.send_message(user_id, text, reply_markup=keyboard)


@BOT.message_handler(func=lambda message: message and message.text and ('✅' in message.text or 'menu' in message.text
                                                                        or '❌' in message.text))
def update_settings(message):
    text = message.text
    user_id = message.from_user.id
    settings = load_settings(user_id)
    if 'Quality' in text:
        settings["stages"]["quality"] = '✅' if settings["stages"]["quality"] == '❌' else '❌'
        save_settings(user_id, settings)
        build_settings_menu(user_id, text='Changed')
    elif 'Highlights' in text:
        settings["stages"]["highlights"] = '✅' if settings["stages"]["highlights"] == '❌' else '❌'
        save_settings(user_id, settings)
        build_settings_menu(user_id, text='Changed')
    elif 'Music' in text:
        settings["stages"]["music_recommendation"] = '✅' if settings["stages"]["music_recommendation"] == '❌' else '❌'
        save_settings(user_id, settings)
        build_settings_menu(user_id, text='Changed')
    elif 'Visbeat' in text:
        settings["stages"]["visbeat"] = '✅' if settings["stages"]["visbeat"] == '❌' else '❌'
        save_settings(user_id, settings)
        build_settings_menu(user_id, text='Changed')
    elif 'Main' in text:
        build_main_menu(user_id)


@BOT.message_handler(commands=['start'])
def check_user(message):
    user_id = str(message.from_user.id)
    user_data_path = os.path.join(os.environ.get('USER_DATA'), user_id)
    if not os.path.exists(user_data_path):  # init user folder
        os.makedirs(user_data_path)
        init_new_folder(user_id)

    BOT.send_message(user_id, 'Hello!\nUpload image, video (max video size 20Mb)')
    build_main_menu(user_id)


@BOT.message_handler(commands=['settings'])
def open_settings(message):
    build_settings_menu(message.chat.id)


@BOT.message_handler(commands=['change_logo'])
def change_logo(message):
    logo = os.environ.get('LOGO', 'default')
    if logo == 'default':
        os.environ['LOGO'] = 'cat'
    else:
        os.environ['LOGO'] = 'default'
    BOT.send_message(message.from_user.id, f'Logo changed to {os.environ["LOGO"]}')


@BOT.message_handler(commands=['create'])
def create_video(message):
    user_id = str(message.from_user.id)
    last_created_folder = get_last_folder_by_id(user_id)
    settings = load_settings(user_id)
    if last_created_folder and glob.glob(f'{last_created_folder}/*/*'):
        WORKER.send({'tgbot': {
            'data_path': last_created_folder,
            'user_id': user_id,
            'logo': os.environ.get('LOGO', 'default'),
            'quality': settings['stages']['quality'] == '✅',
            'highlights': settings['stages']['highlights'] == '✅',
            'music_recommendation': settings['stages']['music_recommendation'] == '✅',
            'visbeat': settings['stages']['visbeat'] == '✅'
        }})
        init_new_folder(user_id)
    else:
        BOT.send_message(message.from_user.id, 'Empty')


@BOT.message_handler(content_types=['photo', 'video', 'video_note', 'document', 'audio'])
def callback_inline_data(message):
    print(message.content_type)
    user_id = str(message.from_user.id)
    folder = None
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        folder = 'images'
    elif message.content_type == 'video':
        file_id = message.video.file_id
        folder = 'videos'
    elif message.content_type == 'audio':
        file_id = message.audio.file_id
        folder = 'audios'
    elif message.content_type == 'document':
        file_id = message.document.file_id
    else:
        return

    file_info = BOT.get_file(file_id)
    print('file.file_path =', file_info.file_path)

    if folder is None:
        folder = get_folder_by_ext(file_info.file_path)

    if folder:
        last_created_folder = get_last_folder_by_id(user_id)
        downloaded_file = BOT.download_file(file_info.file_path)
        with open(os.path.join(last_created_folder, folder, os.path.basename(file_info.file_path)), 'wb') as file:
            file.write(downloaded_file)
    BOT.send_message(user_id, 'Done!')


@BOT.message_handler(commands=['demo'])
def create_video(message):
    user_id = str(message.from_user.id)
    settings = load_settings(user_id)
    WORKER.send({'tgbot': {
        'data_path': '/demo',
        'user_id': user_id,
        'logo': os.environ.get('LOGO', 'default'),
        'quality': settings['stages']['quality'] == '✅',
        'highlights': settings['stages']['highlights'] == '✅',
        'music_recommendation': settings['stages']['music_recommendation'] == '✅',
        'visbeat': settings['stages']['visbeat'] == '✅'
    }})


if __name__ == '__main__':
    os.environ['LOGO'] = 'default'
    while True:
        try:
            WORKER = RabbitMQWorker(None, **RABBIT_CONFIG['tgbot'])
            break
        except Exception as e:
            print(e)
            time.sleep(10)

    BOT.polling(none_stop=True)
