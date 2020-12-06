import glob
import os
import time

import cv2

from common.config import RABBIT_CONFIG, RESULT_VIDEO_PARAMS
from common.rabbit_worker import RabbitMQWorker


def callback(message):
    """Queue callback
    :param message: json data
    """
    print(message, flush=True)
    start_time = time.time()
    # Заглушка
    highlight_path = os.path.join(message["tgbot"]["data_path"], f'test.{RESULT_VIDEO_PARAMS["format"]["ext"]}')
    writer = cv2.VideoWriter(highlight_path,
                             cv2.VideoWriter_fourcc(*RESULT_VIDEO_PARAMS['format']['fourcc']),
                             RESULT_VIDEO_PARAMS['fps'],
                             RESULT_VIDEO_PARAMS['size'])
    for file_path in glob.glob(f'{message["tgbot"]["data_path"]}/*'):
        if file_path != highlight_path:
            image = cv2.imread(file_path)
            image = cv2.resize(image, (1280, 720))
            for _ in range(200):
                writer.write(image)
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
