import time

from common.config import RABBIT_CONFIG
from common.rabbit_worker import RabbitMQWorker
from common.telegram import send_message


def callback(message):
    """Queue callback
    :param message: json data
    """
    print(message, flush=True)
    start_time = time.time()
    send_message('Stage 3/4', message['tgbot']['user_id'])

    audio_path = 'http://f.find-music.net/music/_Rokki%201%20(Rocky)/Bill%20Conti%20-%20Gonna%20Fly%20Now%20(Theme%20from%20Rocky).mp3'

    message.update({'music_recommendation': {'audio_path': audio_path,
                                             'time': time.time() - start_time}})
    send_message(f'Stage 3/4, time: {message["music_recommendation"]["time"]}', message['tgbot']['user_id'])
    return message


if __name__ == '__main__':
    while True:
        try:
            worker = RabbitMQWorker(callback, **RABBIT_CONFIG['music_recommendation'])
            worker.listen_queue()
        except Exception as e:
            print(e, flush=True)
        time.sleep(10)
