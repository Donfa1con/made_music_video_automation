import glob
import random
import time

import cv2

from common.config import RABBIT_CONFIG, RESULT_VIDEO_PARAMS
from common.rabbit_worker import RabbitMQWorker
from common.telegram import send_message, send_video
from common.utils import create_writer, resize_image_with_ratio


def callback(message):
    """Queue callback
    :param message: json data
    """
    print(message, flush=True)
    start_time = time.time()
    send_message("Stage 2/4", message['tgbot']['user_id'])
    # Заглушка
    bad_writer, bad_frames_path = create_writer(message["tgbot"]["data_path"], 'bad_frames')
    writer, highlight_path = create_writer(message["tgbot"]["data_path"], 'highlights')

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
                image = resize_image_with_ratio(image, *RESULT_VIDEO_PARAMS['size'])
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
                    resized_frame = resize_image_with_ratio(frame, *RESULT_VIDEO_PARAMS['size'])
                    if frame_cnt in good_frames:
                        writer.write(resized_frame)
                    else:
                        bad_writer.write(resized_frame)
                    frame_cnt += 1
                cap.release()
        else:
            if file_path in images_paths:
                image = cv2.imread(file_path)
                image = resize_image_with_ratio(image, *RESULT_VIDEO_PARAMS['size'])
                for _ in range(int(RESULT_VIDEO_PARAMS['fps'] // 3)):
                    bad_writer.write(image)

    writer.release()
    bad_writer.release()

    send_video(bad_frames_path, message['tgbot']['user_id'])
    message.update({'highlights': {'time': time.time() - start_time,
                                   'highlight_path': highlight_path}})
    send_message(f'Stage 2/4, time: {message["highlights"]["time"]}', message['tgbot']['user_id'])
    return message


if __name__ == '__main__':
    while True:
        try:
            worker = RabbitMQWorker(callback, **RABBIT_CONFIG['highlights'])
            worker.listen_queue()
        except Exception as e:
            print(e)
        time.sleep(10)
