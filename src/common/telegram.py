import os
import requests


def send_video(video_path, user_id):
    bot_url = 'https://api.telegram.org/bot{}/sendVideo?chat_id={}&caption={}'.format(os.environ.get("BOT_TOKEN"),
                                                                                      user_id, "Video created")
    with open(video_path, 'rb') as video:
        r = requests.post(bot_url, files={'video': video})
        print(r.text, flush=True)


def send_message(text, user_id):
    bot_url = f'https://api.telegram.org/bot{os.environ.get("BOT_TOKEN")}/sendMessage?chat_id={user_id}&text={text}'
    r = requests.post(bot_url)
    print(r.text, flush=True)
