FROM python:2.7
USER root

RUN apt update && apt-get install libsndfile1 python-opencv -y

WORKDIR /code
COPY cat.png /usr/local/lib/python2.7/site-packages/visbeat/_assets/images/

COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code

ENV PYTHONUNBUFFERED=1

CMD python main.py