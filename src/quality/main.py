import collections
import glob
import time

import cv2

from common.config import RABBIT_CONFIG, QUALITY_THRESHOLD, RESULT_VIDEO_PARAMS
from common.rabbit_worker import RabbitMQWorker
from common.telegram import send_message, send_video
from model import QualityModel
from common.utils import create_writer, resize_image_with_ratio


def callback(message):
    """Queue callback
    :param message: json data
    """
    print(message, flush=True)
    start_time = time.time()
    send_message('Stage 1/4', message['tgbot']['user_id'])

    message['quality'] = {'results': collections.defaultdict(list)}

    writer, bad_frames_path = create_writer(message["tgbot"]["data_path"], 'bad_frames')

    images_paths = glob.glob(f'{message["tgbot"]["data_path"]}/images/*')
    for image_path in images_paths:
        image = cv2.imread(image_path)
        score = QUALITY_MODEL.predict(image)
        if score > QUALITY_THRESHOLD:
            message['quality']['results'][image_path].append(True)
        else:
            resized_frame = resize_image_with_ratio(image, *RESULT_VIDEO_PARAMS['size'])
            for _ in range(int(RESULT_VIDEO_PARAMS['fps'] // 3)):
                writer.write(resized_frame)

    videos_paths = glob.glob(f'{message["tgbot"]["data_path"]}/videos/*')
    for video_path in videos_paths:
        cap = cv2.VideoCapture(video_path)
        frame_cnt = 0
        while True:
            success, frame = cap.read()
            if not success:
                break
            score = QUALITY_MODEL.predict(frame)
            if score > QUALITY_THRESHOLD:
                message['quality']['results'][video_path].append(frame_cnt)
            else:
                resized_frame = resize_image_with_ratio(frame, *RESULT_VIDEO_PARAMS['size'])
                writer.write(resized_frame)
            frame_cnt += 1
        cap.release()
    writer.release()

    send_video(bad_frames_path, message['tgbot']['user_id'])
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
