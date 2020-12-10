import time

import utils
from common.config import RABBIT_CONFIG
from common.rabbit_worker import RabbitMQWorker
from common.telegram import send_message, send_video


def callback(message):
    """Queue callback
    :param message: json data
    """
    print(message)
    start_time = time.time()
    send_message('Stage 4/4', message['tgbot']['user_id'])

    message.update({'video_audio_compose': {'time': time.time() - start_time}})

    utils.update_logo(message['tgbot']['logo'])
    highlight_path = utils.dancify(message['highlights']['highlight_path'],
                                   message['music_recommendation']['audio_path'],
                                   message['tgbot']['user_id'])

    send_message('Stage 4/4, time: {0:.2f}'.format(time.time() - start_time), message['tgbot']['user_id'])
    send_video(highlight_path, message['tgbot']['user_id'])
    return message


if __name__ == '__main__':
    while True:
        try:
            worker = RabbitMQWorker(callback, **RABBIT_CONFIG['video_audio_compose'])
            worker.listen_queue()
        except Exception as e:
            print(e)
        time.sleep(10)
