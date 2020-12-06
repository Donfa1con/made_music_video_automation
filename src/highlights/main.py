import glob
import os
import time
import random

import cv2

from common.config import RABBIT_CONFIG, RESULT_VIDEO_PARAMS
from common.rabbit_worker import RabbitMQWorker
import utils
from common.telegram import send_message


def create_writer(message):
    highlight_path = os.path.join(message["tgbot"]["data_path"], f'test.{RESULT_VIDEO_PARAMS["format"]["ext"]}')
    writer = cv2.VideoWriter(highlight_path,
                             cv2.VideoWriter_fourcc(*RESULT_VIDEO_PARAMS['format']['fourcc']),
                             RESULT_VIDEO_PARAMS['fps'],
                             RESULT_VIDEO_PARAMS['size'])
    return writer, highlight_path


def callback(message):
    """Queue callback
    :param message: json data
    """
    print(message, flush=True)
    start_time = time.time()
    send_message("Stage 2/4", message['tgbot']['user_id'])
    # Заглушка
    writer, highlight_path = create_writer(message)

    images_paths = glob.glob(f'{message["tgbot"]["data_path"]}/images/*')
    videos_paths = glob.glob(f'{message["tgbot"]["data_path"]}/videos/*')
    all_paths = images_paths + videos_paths
    random.shuffle(all_paths)
    images_paths = set(images_paths)
    videos_paths = set(videos_paths)

    for file_path in all_paths:
        if file_path in message['quality']['results']:
            if file_path in images_paths:
                image = cv2.imread(file_path)
                image = utils.resize_image_with_ratio(image, *RESULT_VIDEO_PARAMS['size'])
                for _ in range(int(RESULT_VIDEO_PARAMS['fps'])):
                    writer.write(image)

            elif file_path in videos_paths:
                cap = cv2.VideoCapture(file_path)
                frame_cnt = 0
                good_frames = set(message['quality']['results'][file_path])
                while True:
                    success, frame = cap.read()
                    if not success:
                        break
                    if frame_cnt in good_frames:
                        resized_frame = utils.resize_image_with_ratio(frame, *RESULT_VIDEO_PARAMS['size'])
                        writer.write(resized_frame)
                    frame_cnt += 1
                cap.release()
    writer.release()
    # Заглушка
    message.update({'highlights': {'time': time.time() - start_time,
                                   'highlight_path': highlight_path}})
    return message


if __name__ == '__main__':
    while True:
        try:
            worker = RabbitMQWorker(callback, **RABBIT_CONFIG['highlights'])
            worker.listen_queue()
        except Exception as e:
            print(e)
        time.sleep(10)
