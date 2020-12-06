import os
import time
import requests

from common.config import RABBIT_CONFIG
from common.rabbit_worker import RabbitMQWorker


def callback(message):
    """Queue callback
    :param message: json data
    """
    print(message, flush=True)
    start_time = time.time()
    message.update({'video_audio_compose': {'time': time.time() - start_time}})

    bot_url = 'https://api.telegram.org/bot{}/sendVideo?chat_id={}&caption={}'.format(os.environ.get("BOT_TOKEN"),
                                                                                      message['tgbot']['user_id'],
                                                                                      "Video created")
    with open(message['highlights']['highlight_path'], 'rb') as video:
        r = requests.post(bot_url, files={'video': video})
        print(r.text, flush=True)
    return message


if __name__ == '__main__':
    while True:
        try:
            worker = RabbitMQWorker(callback, **RABBIT_CONFIG['video_audio_compose'])
            worker.listen_queue()
        except Exception as e:
            print(e, flush=True)
        time.sleep(10)
