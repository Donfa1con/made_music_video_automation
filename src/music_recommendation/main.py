import time

from common.config import RABBIT_CONFIG
from common.rabbit_worker import RabbitMQWorker


def callback(message):
    """Queue callback
    :param message: json data
    """
    print(message, flush=True)
    start_time = time.time()
    message.update({'music_recommendation': {'time': time.time() - start_time}})
    return message


if __name__ == '__main__':
    while True:
        try:
            worker = RabbitMQWorker(callback, **RABBIT_CONFIG['music_recommendation'])
            worker.listen_queue()
        except Exception as e:
            print(e, flush=True)
        time.sleep(10)