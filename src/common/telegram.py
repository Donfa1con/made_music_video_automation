import os
import requests


def send_video(video_path, user_id, text="Video created", ):
    bot_url = 'https://api.telegram.org/bot{0}/sendVideo?chat_id={1}&caption={2}'.format(os.environ.get("BOT_TOKEN"),
                                                                                         user_id, text)
    with open(video_path, 'rb') as video:
        r = requests.post(bot_url, files={'video': video})
        print(r.text)


def send_message(text, user_id):
    bot_url = 'https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}'.format(os.environ.get("BOT_TOKEN"),
                                                                                        user_id, text)
    r = requests.post(bot_url)
    print(r.text)
