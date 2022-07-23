FROM python:3-slim

ARG PORT
ENV PORT=${PORT:-80}

ARG VERSION
ENV VERSION=${VERSION}

RUN pip install pipenv uvicorn

WORKDIR /app

COPY ./Pipfile ./Pipfile.lock /app/

RUN pipenv install --deploy --ignore-pipfile --system

COPY ./app /app/app/

EXPOSE ${PORT}

CMD uvicorn app:app --proxy-headers --host 0.0.0.0 --port $PORT
