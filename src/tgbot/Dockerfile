FROM openvino/ubuntu18_runtime:2021.1
USER root
RUN rm -r /opt/intel/openvino/opencv/ && \
    rm /opt/intel/openvino/python/python3/cv2.abi3.so && \
    apt update && apt-get install libgl1-mesa-dev -y

WORKDIR /code

COPY requirements.txt /code/
RUN pip3 install -r requirements.txt

COPY . /code

ENV PYTHONUNBUFFERED=1

CMD python3 main.py