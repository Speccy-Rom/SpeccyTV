#!/bin/sh

wait_for_service() {
  local name="$1" host="$2" port="$3" retry_interval="$4"
  echo "Waiting for $name..."
  while ! nc -z $host $port; do
    sleep $retry_interval
  done
  echo "$name started"
}

wait_for_service "Postgres_Auth" $POSTGRES_AUTH_HOST $POSTGRES_AUTH_PORT 0.5
wait_for_service "Redis_Auth" $REDIS_AUTH_HOST $REDIS_AUTH_PORT 0.5

flask db upgrade
flask app init
flask superuser delete --email $AUTH_ADMIN_EMAIL
flask superuser create --email $AUTH_ADMIN_EMAIL --first-name $AUTH_ADMIN_FIRST_NAME \
                       --last-name $AUTH_ADMIN_LAST_NAME --password $AUTH_ADMIN_PASSWORD

exec "$@"