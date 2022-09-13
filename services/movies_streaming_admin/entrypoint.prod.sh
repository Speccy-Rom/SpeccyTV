#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 0.1s
done

echo "PostgreSQL started"

python manage.py flush --no-input
python manage.py collectstatic --no-input --clear
python manage.py makemigrations --no-input
python manage.py migrate --noinput

echo "from django.contrib.auth.models import User;
User.objects.filter(email='$DJANGO_ADMIN_EMAIL').delete();
User.objects.create_superuser('$DJANGO_ADMIN_USERNAME', '$DJANGO_ADMIN_EMAIL', '$DJANGO_ADMIN_PASSWORD');
" | python manage.py shell

echo "Django superuser $DJANGO_ADMIN_USERNAME created"

exec "$@"