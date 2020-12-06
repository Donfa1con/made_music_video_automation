import glob
import os
import time

import telebot

from common.config import RABBIT_CONFIG
from common.rabbit_worker import RabbitMQWorker

BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise Exception("BOT_TOKEN is undefined")
BOT = telebot.TeleBot(BOT_TOKEN)


def get_last_folder_by_id(user_id):
    user_data_path = os.path.join(os.environ.get('USER_DATA'), user_id)
    all_folders = glob.glob(f'{user_data_path}/*')
    if all_folders:
        return max(all_folders, key=os.path.getmtime)


def init_new_folder(user_id):
    user_data_path = os.path.join(os.environ.get('USER_DATA'), user_id)
    new_folder_name = os.path.join(user_data_path, str(int(time.time())))
    os.makedirs(os.path.join(new_folder_name, 'videos'))
    os.makedirs(os.path.join(new_folder_name, 'images'))


def get_folder_by_ext(path):
    ext = os.path.splitext(os.path.basename(path))[1]
    if ext in ['.mp4']:
        return 'videos'
    if ext in ['.jpeg', '.jpg']:
        return 'images'


@BOT.message_handler(commands=['start'])
def check_user(message):
    BOT.send_message(message.from_user.id, 'Hello')


@BOT.message_handler(commands=['create'])
def check_user(message):
    user_id = str(message.from_user.id)
    last_created_folder = get_last_folder_by_id(user_id)
    if last_created_folder and glob.glob(f'{last_created_folder}/*/*'):
        WORKER.send({'tgbot': {
            'data_path': last_created_folder,
            'user_id': user_id
        }})
        init_new_folder(user_id)
    else:
        BOT.send_message(message.from_user.id, 'Empty')


@BOT.message_handler(content_types=['photo', 'video', 'video_note', 'document'])
def callback_inline_photo(message):
    print(message.content_type)

    user_id = str(message.from_user.id)
    user_data_path = os.path.join(os.environ.get('USER_DATA'), user_id)
    if not os.path.exists(user_data_path):  # init user folder
        os.makedirs(user_data_path)
        init_new_folder(user_id)

    folder = None
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        folder = 'images'
    elif message.content_type == 'document':
        file_id = message.document.file_id
    else:
        return

    file_info = BOT.get_file(file_id)
    print('file.file_path =', file_info.file_path, flush=True)

    if folder is None:
        folder = get_folder_by_ext(file_info.file_path)

    if folder:
        last_created_folder = get_last_folder_by_id(user_id)
        downloaded_file = BOT.download_file(file_info.file_path)
        with open(os.path.join(last_created_folder, folder, os.path.basename(file_info.file_path)), 'wb') as file:
            file.write(downloaded_file)


if __name__ == '__main__':
    while True:
        try:
            WORKER = RabbitMQWorker(None, **RABBIT_CONFIG['tgbot'])
            break
        except Exception as e:
            print(e, flush=True)
            time.sleep(10)
    BOT.polling(none_stop=True)
