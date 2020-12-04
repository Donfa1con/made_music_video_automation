import glob
import os
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
    # Заглушка
    highlight_path = os.path.join(message["tgbot"]["data_path"], 'test.mp4')
    writer = cv2.VideoWriter(highlight_path, cv2.VideoWriter_fourcc(*'mp4v'), 20.0, (640, 480))
    for file_path in glob.glob(f'{message["tgbot"]["data_path"]}/*'):
        if file_path != highlight_path:
            image = cv2.imread(file_path)
            cv2.resize(image, (640, 480))
            for _ in range(20):
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
