web: python manage.py makemigrations voting && python manage.py migrate && python manage.py collectstatic --noinput && daphne -b 0.0.0.0 -p $PORT oxvote.asgi:application
