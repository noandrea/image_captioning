# https://github.com/DeepRNN/image_captioning

FROM debian:buster-slim

RUN apt update && apt install -y \
  python3-pip python3-dev python-virtualenv vim curl git apt-utils


RUN pip install numpy \
  opencv-python-headless \
  opencv-contrib-python-headless \
  scipy \ 
  matplotlib \
  ipython \
  jupyter \
  pandas \
  sympy \
  nose \
  tqdm \
  tensorflow

RUN mkdir /data && git clone https://github.com/DeepRNN/image_captioning /data/image_catpioning

WORKDIR /data/image_catpioning
ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
