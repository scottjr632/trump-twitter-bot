FROM python:3.6.8-slim-stretch

RUN mkdir /trump-bot

COPY ./requirements.txt /trump-bot/requirements.txt

WORKDIR /trump-bot

RUN pip3 install -r requirements.txt

COPY . /trump-bot

ENTRYPOINT [ "python", "main.py" ]