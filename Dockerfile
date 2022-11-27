FROM python:3.8-alpine

COPY Pipfile* /tkgbot/
WORKDIR /tkgbot

RUN apk update && apk add python3-dev \
                        gcc \
                        libc-dev

RUN pip install pipenv && pipenv sync

COPY . /tkgbot

RUN mkdir data; if [ ! -f data/data.sqlite3 ]; then pipenv run python -c "import tkgbot.database; tkgbot.database.init_db()"; fi

ENTRYPOINT ["pipenv", "run", "python", "-m", "tkgbot"]
