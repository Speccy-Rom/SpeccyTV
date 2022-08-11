#!/bin/sh

echo "from django.contrib.auth.models import User;
User.objects.filter(email='$DJANGO_ADMIN_EMAIL').delete();
User.objects.create_superuser('$DJANGO_ADMIN_USERNAME', '$DJANGO_ADMIN_EMAIL', '$DJANGO_ADMIN_PASSWORD');
" | python manage.py shell

echo "Django superuser $DJANGO_ADMIN_USERNAME created"

exec "$@"
