FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN apt update && apt install inotify-tools -y && apt install ffmpeg -y

RUN pip install -r requirements.txt

CMD ./run.sh