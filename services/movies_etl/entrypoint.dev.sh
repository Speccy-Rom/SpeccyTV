#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 0.1s
done

echo "PostgreSQL started"

echo "Waiting for elasticsearch..."

while ! nc -z "$ELASTICSEARCH_HOST" "$ELASTICSEARCH_PORT"; do
  sleep 0.1s
done

echo "Elasticsearch started"

exec "$@"