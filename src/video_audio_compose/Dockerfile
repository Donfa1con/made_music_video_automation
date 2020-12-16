FROM python:2.7
USER root

RUN apt update && apt-get install libsndfile1 python-opencv libgl1-mesa-dev ffmpeg -y

WORKDIR /code

COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY cat.png /usr/local/lib/python2.7/site-packages/visbeat/_assets/images/cat.png
COPY default.png /usr/local/lib/python2.7/site-packages/visbeat/_assets/images/default.png

COPY . /code

ENV PYTHONUNBUFFERED=1

CMD python main.py