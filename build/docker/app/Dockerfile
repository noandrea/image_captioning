# https://github.com/DeepRNN/image_captioning

FROM debian:buster-slim

RUN apt update && apt install -y \
  python3-pip python3-dev python-virtualenv vim curl git apt-utils python3-tk libsm6 libxext6


RUN pip3 install numpy \
  opencv-python \
  opencv-contrib-python \
  scipy \
  matplotlib \
  ipython \
  jupyter \
  pandas \
  sympy \
  nose \
  tqdm \
  tensorflow \
  scikit-image \
  nltk \
  psycopg2 \
  pynacl \
  flask \
  flask_socketio \
  eventlet \
  flask \
  flask-socketio

RUN python3 -m nltk.downloader punkt

RUN mkdir /data 
COPY . /data

WORKDIR /data
ENTRYPOINT ["python3", "anna.py"]
CMD ["start", "-c", "/data/settings.json"]
