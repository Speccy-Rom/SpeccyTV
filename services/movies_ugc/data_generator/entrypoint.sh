#!/bin/sh
echo "Kafka not yet run..."
while ! nc -z $KAFKA_HOST $KAFKA_PORT; do
  sleep 0.1
done
echo "Kafka did run."
python main.py
exec "$@"
