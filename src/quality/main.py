import collections
import glob
import random
import time

import cv2

from common.config import RABBIT_CONFIG
from common.rabbit_worker import RabbitMQWorker


def callback(message):
    """Queue callback
    :param message: json data
    """
    print(message, flush=True)
    start_time = time.time()

    message['quality'] = {'results': collections.defaultdict(list)}

    images_paths = glob.glob(f'{message["tgbot"]["data_path"]}/images/*')
    for image_path in images_paths:
        if random.random() > 0:
            message['quality']['results'][image_path].append(True)

    videos_paths = glob.glob(f'{message["tgbot"]["data_path"]}/videos/*')
    for video_path in videos_paths:
        cap = cv2.VideoCapture(video_path)
        frame_cnt = 0
        while True:
            success, frame = cap.read()
            if not success:
                break
            if random.random() > 0.9:
                message['quality']['results'][video_path].append(frame_cnt)
            frame_cnt += 1
        cap.release()

    message['quality'].update({'time': time.time() - start_time})
    return message


if __name__ == '__main__':
    while True:
        try:
            worker = RabbitMQWorker(callback, **RABBIT_CONFIG['quality'])
            worker.listen_queue()
        except Exception as e:
            print(e, flush=True)
        time.sleep(10)
