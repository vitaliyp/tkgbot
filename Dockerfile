FROM python:3.7-alpine

COPY Pipfile* /tkgbot/
WORKDIR /tkgbot

RUN pip install pipenv && pipenv sync

COPY . /tkgbot

RUN mkdir data; if [ ! -f data/data.sqlite3 ]; then pipenv run python -c "import tkgbot.database; tkgbot.database.init_db()"; fi

ENTRYPOINT ["pipenv", "run", "python", "-m", "tkgbot"]
