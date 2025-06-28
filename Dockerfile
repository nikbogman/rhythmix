FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg build-essential libeigen3-dev libyaml-dev libfftw3-dev libavcodec-dev libavformat-dev libavutil-dev libswresample-dev libsamplerate0-dev libtag1-dev libchromaprint-dev

WORKDIR /rhythmix

COPY ./requirements.txt /rhythmix/requirements.txt

RUN pip install --no-cache-dir -r /rhythmix/requirements.txt

COPY ./app /rhythmix/app
COPY ./static /rhythmix/static

CMD ["fastapi", "run", "app/main.py"]