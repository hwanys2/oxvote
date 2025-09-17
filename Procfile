web: rm -f db.sqlite3 && rm -rf voting/migrations/0*.py && python manage.py makemigrations voting && python manage.py migrate && gunicorn oxvote.wsgi --log-file -
