# Backend

Start app:
``` bash
# Create database
$ python manage.py makemigrations restapi && python manage.py migrate restapi && python manage.py makemigrations&& python manage.py migrate
# Run server
$ python manage.py runserver
```

If you have applied migrations you would like to delete run the following command:
``` bash
$ rm db.sqlite3 && rm -r restapi/migrations
```