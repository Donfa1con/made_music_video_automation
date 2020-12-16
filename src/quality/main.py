import collections
import glob
import os
import time

import cv2
import numpy as np

from common.config import RABBIT_CONFIG
from common.rabbit_worker import RabbitMQWorker
from common.telegram import send_message
from model import QualityModel


def callback(message):
    """Queue callback
    :param message: json data
    """
    print(message)
    start_time = time.time()
    send_message('Stage 1/4', message['tgbot']['user_id'])

    message['quality'] = {'results': collections.defaultdict(list)}
    if message['tgbot']['quality']:
        max_frame_for_reading = float(os.environ.get('MAX_FRAMES_FOR_READING', float('inf')))
        total_frames = 0
        images_paths = glob.glob(f'{message["tgbot"]["data_path"]}/images/*')
        scores = []
        for image_path in images_paths:
            image = cv2.imread(image_path)
            score = QUALITY_MODEL.predict(image)
            scores.append(score)
            message['quality']['results'][image_path].append(score)

        videos_paths = glob.glob(f'{message["tgbot"]["data_path"]}/videos/*')
        for video_path in videos_paths:
            if total_frames > max_frame_for_reading:
                break

            cap = cv2.VideoCapture(video_path)
            frame_cnt = 0
            while True:
                success, frame = cap.read()
                if not success:
                    break
                if frame_cnt % 3 == 1:
                    score = QUALITY_MODEL.predict(frame)
                    scores.extend([score, score, score])
                    message['quality']['results'][video_path].extend([score, score, score])
                frame_cnt += 1

                total_frames += 1
                if total_frames > max_frame_for_reading:
                    break
            cap.release()

        quality_threshold = float(os.environ.get('QUALITY_THRESHOLD', np.median(scores)))

        for key, val in message['quality']['results'].items():
            frame_ids = []
            for idx, v in enumerate(val):
                if v < quality_threshold:
                    frame_ids.append(idx)
            message['quality']['results'][key] = frame_ids
    message['quality'].update({'time': time.time() - start_time})
    send_message(f'Stage 1/4, time: {message["quality"]["time"]:.2f}', message['tgbot']['user_id'])
    return message


if __name__ == '__main__':
    QUALITY_MODEL = QualityModel('models/hyper_net')
    while True:
        try:
            worker = RabbitMQWorker(callback, **RABBIT_CONFIG['quality'])
            worker.listen_queue()
        except Exception as e:
            print(e)
        time.sleep(10)
