import os
import time

from common.config import RABBIT_CONFIG
from common.rabbit_worker import RabbitMQWorker
import ffmpeg
from common.telegram import send_video, send_message


def add_audio(video_path, audio_path):
    video_part = ffmpeg.input(video_path)
    audio_part = ffmpeg.input(audio_path)
    video_path = os.path.splitext(video_path)
    video_path = f'{video_path[0]}_music{video_path[1]}'
    ffmpeg.output(audio_part.audio, video_part.video, video_path, shortest=None, vcodec='copy').run()
    return video_path


def callback(message):
    """Queue callback
    :param message: json data
    """
    print(message, flush=True)
    start_time = time.time()
    send_message('Stage 4/4', message['tgbot']['user_id'])

    message.update({'video_audio_compose': {'time': time.time() - start_time}})

    highlight_path = add_audio(message['highlights']['highlight_path'],
                               message['music_recommendation']['audio_path'])

    send_message(f'Stage 4/4, time: {time.time() - start_time}', message['tgbot']['user_id'])
    send_video(highlight_path, message['tgbot']['user_id'])
    return message


if __name__ == '__main__':
    while True:
        try:
            worker = RabbitMQWorker(callback, **RABBIT_CONFIG['video_audio_compose'])
            worker.listen_queue()
        except Exception as e:
            print(e, flush=True)
        time.sleep(10)
