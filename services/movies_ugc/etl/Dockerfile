# pull official base image
FROM python:3.9-alpine
# set work directory
WORKDIR /usr/src/etl
# install dependencies
RUN apk update --no-cache \
    && apk add gcc musl-dev python3-dev libffi-dev
RUN pip install --upgrade pip poetry
COPY ./pyproject.toml .
RUN poetry config virtualenvs.create false
RUN poetry install
# copy project
COPY . .
ENTRYPOINT ["sh", "/usr/src/etl/entrypoint.sh"]
