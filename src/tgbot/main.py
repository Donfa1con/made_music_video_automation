import glob
import os
import time
import uuid

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


@BOT.message_handler(commands=['start'])
def check_user(message):
    BOT.send_message(message.from_user.id, 'Hello')


@BOT.message_handler(commands=['create'])
def check_user(message):
    user_id = str(message.from_user.id)
    last_created_folder = get_last_folder_by_id(user_id)
    if last_created_folder and glob.glob(f'{last_created_folder}/*'):
        WORKER.send({'tgbot': {
            'data_path': last_created_folder,
            'user_id': user_id
        }})
        os.makedirs(os.path.join(os.environ.get('USER_DATA'), user_id, str(int(time.time()))))
    else:
        BOT.send_message(message.from_user.id, 'Empty')


@BOT.message_handler(content_types=['photo'])
def callback_inline(message):
    user_id = str(message.from_user.id)
    user_data_path = os.path.join(os.environ.get('USER_DATA'), user_id)
    if not os.path.exists(user_data_path):  # init user folder
        os.makedirs(user_data_path)
        os.makedirs(os.path.join(user_data_path, str(int(time.time()))))

    file_id = message.photo[-1].file_id
    file_info = BOT.get_file(file_id)
    print('file.file_path =', file_info.file_path, flush=True)

    last_created_folder = get_last_folder_by_id(user_id)

    downloaded_file = BOT.download_file(file_info.file_path)
    with open(os.path.join(last_created_folder, uuid.uuid4().hex) + '.jpg', 'wb') as file:
        file.write(downloaded_file)


if __name__ == '__main__':
    while True:
        try:
            WORKER = RabbitMQWorker(None, **RABBIT_CONFIG['tgbot'])
            break
        except Exception as e:
            time.sleep(10)
    BOT.polling(none_stop=True)
