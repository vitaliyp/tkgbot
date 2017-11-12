FROM python:3.6.3-alpine

COPY . /tkgbot
WORKDIR /tkgbot

RUN pip install pipenv && pipenv install

CMD ["pipenv", "run", "python", "app.py"]
