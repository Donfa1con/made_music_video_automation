import collections
import glob
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
    print(message, flush=True)
    start_time = time.time()
    send_message('Stage 1/4', message['tgbot']['user_id'])

    message['quality'] = {'results': collections.defaultdict(list)}

    images_paths = glob.glob(f'{message["tgbot"]["data_path"]}/images/*')
    scores = []
    for image_path in images_paths:
        image = cv2.imread(image_path)
        score = QUALITY_MODEL.predict(image)
        scores.append(score)
        message['quality']['results'][image_path].append(score)

    videos_paths = glob.glob(f'{message["tgbot"]["data_path"]}/videos/*')
    for video_path in videos_paths:
        cap = cv2.VideoCapture(video_path)
        frame_cnt = 0
        while True:
            success, frame = cap.read()
            if not success:
                break
            score = QUALITY_MODEL.predict(frame)
            scores.append(score)
            message['quality']['results'][video_path].append(frame_cnt)

            frame_cnt += 1
        cap.release()

    quality_threshold = np.median(scores)

    for key, val in message['quality']['results'].items():
        frame_ids = []
        for idx, v in enumerate(val):
            if v > quality_threshold:
                frame_ids.append(idx)
        message['quality']['results'][key] = frame_ids

    message['quality'].update({'time': time.time() - start_time})
    send_message(f'Stage 1/4, time: {message["quality"]["time"]}', message['tgbot']['user_id'])
    return message


if __name__ == '__main__':
    QUALITY_MODEL = QualityModel('models/hyper_net')
    while True:
        try:
            worker = RabbitMQWorker(callback, **RABBIT_CONFIG['quality'])
            worker.listen_queue()
        except Exception as e:
            print(e, flush=True)
        time.sleep(10)
