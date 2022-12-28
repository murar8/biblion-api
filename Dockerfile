# TODO: Using alpine works fine in 3.10 but fails using 3.11.
# FROM python:3.11-alpine

FROM python:3.11-slim

ARG PORT
ENV PORT=${PORT}

ARG VERSION
ENV VERSION=${VERSION}

RUN useradd --system --no-create-home python

RUN pip install --no-cache --upgrade pip && pip install --no-cache pipenv uvicorn

WORKDIR /app

COPY ./Pipfile ./Pipfile.lock /app/

RUN pipenv install --deploy --ignore-pipfile --system --clear

COPY ./app /app/app/

USER python

EXPOSE ${PORT}

CMD uvicorn app:app --proxy-headers --host 0.0.0.0 --port $PORT
