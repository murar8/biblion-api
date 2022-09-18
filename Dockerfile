FROM python:3-alpine

ARG PORT
ENV PORT=${PORT}

ARG VERSION
ENV VERSION=${VERSION}

RUN adduser -S python

RUN pip install --no-cache --upgrade pip && pip install --no-cache pipenv uvicorn

WORKDIR /app

COPY ./Pipfile ./Pipfile.lock /app/

RUN pipenv install --deploy --ignore-pipfile --system --clear

COPY ./app /app/app/

USER python

EXPOSE ${PORT}

CMD uvicorn app:app --proxy-headers --host 0.0.0.0 --port $PORT
