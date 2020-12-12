import collections
import glob
import os
import random
import time

import cv2

from common.config import RABBIT_CONFIG, RESULT_VIDEO_PARAMS
from common.rabbit_worker import RabbitMQWorker
from common.telegram import send_message, send_video
from common.utils import create_writer, resize_image_with_ratio
from model import Video2GifModel


def callback(message):
    """Queue callback
    :param message: json data
    """
    print(message)
    start_time = time.time()
    send_message("Stage 2/4", message['tgbot']['user_id'])

    bad_writer, bad_frames_path = create_writer(message["tgbot"]["data_path"], 'bad_frames')

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
                image = VIDE2GIF.preprocess(image)
                _ = VIDE2GIF.predict_image(image, file_path)
            elif file_path in videos_paths:
                cap = cv2.VideoCapture(file_path)
                frame_cnt = 0
                good_frames = set(message['quality']['results'][file_path])
                queue = collections.deque(maxlen=VIDE2GIF.deep)
                q_size = 0
                while True:
                    success, frame = cap.read()
                    if not success:
                        break
                    if frame_cnt in good_frames:
                        resized_frame = VIDE2GIF.preprocess(frame)
                        queue.append(resized_frame)
                        q_size += 1
                        if q_size == VIDE2GIF.deep:
                            q_size = VIDE2GIF.deep // 2
                            _ = VIDE2GIF.predict_clip(queue, file_path)
                    else:
                        resized_frame = resize_image_with_ratio(frame, *RESULT_VIDEO_PARAMS['size'])
                        bad_writer.write(resized_frame)
                    frame_cnt += 1
                cap.release()
        else:
            if file_path in images_paths:
                image = cv2.imread(file_path)
                image = resize_image_with_ratio(image, *RESULT_VIDEO_PARAMS['size'])
                for _ in range(int(RESULT_VIDEO_PARAMS['fps'] // 3)):
                    bad_writer.write(image)
    bad_writer.release()
    send_video(bad_frames_path, os.environ.get('ADMIN_CHANNEL'), 'Low quality frames')
    total_video_params = VIDE2GIF.get_best_scores(int(os.environ.get('MAX_RESULT_VIDEO_LENGTH')))
    writer, highlight_path = create_writer(message["tgbot"]["data_path"], 'highlights')

    for file_path in all_paths:
        if file_path in total_video_params:
            if file_path in images_paths:
                image = cv2.imread(file_path)
                image = resize_image_with_ratio(image, *RESULT_VIDEO_PARAMS['size'])
                for _ in range(int(RESULT_VIDEO_PARAMS['fps'])):
                    writer.write(image)

            elif file_path in videos_paths:
                cap = cv2.VideoCapture(file_path)
                frame_cnt = 0
                frame_cnt_good_frames = 0
                scored_frames = set(total_video_params[file_path])
                good_frames = set(message['quality']['results'][file_path])
                while scored_frames:
                    success, frame = cap.read()
                    if not success:
                        break
                    if frame_cnt in good_frames:
                        if frame_cnt_good_frames in scored_frames:
                            resized_frame = resize_image_with_ratio(frame, *RESULT_VIDEO_PARAMS['size'])
                            scored_frames.remove(frame_cnt_good_frames)
                            writer.write(resized_frame)
                        frame_cnt_good_frames += 1
                    frame_cnt += 1
                cap.release()
    writer.release()
    message.update({'highlights': {'time': time.time() - start_time,
                                   'highlight_path': highlight_path}})
    send_message(f'Stage 2/4, time: {message["highlights"]["time"]:.2f}', message['tgbot']['user_id'])
    return message


if __name__ == '__main__':
    VIDE2GIF = Video2GifModel('models/video2gif', 'models/snipplet_mean.npy')
    while True:
        try:
            worker = RabbitMQWorker(callback, **RABBIT_CONFIG['highlights'])
            worker.listen_queue()
        except Exception as e:
            print(e)
        time.sleep(10)
