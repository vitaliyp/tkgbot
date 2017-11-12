FROM python:3.6.3-alpine

COPY Pipfile* /tkgbot/
WORKDIR /tkgbot

RUN pip install pipenv && pipenv install

COPY . /tkgbot

RUN mkdir data; if [ ! -f data/data.sqlite3 ]; then pipenv run python -c "import database; database.init_db()"; fi

ENTRYPOINT ["pipenv", "run", "python", "app.py"]
