# Backend

Start app:
``` bash
# Create database
$ python manage.py makemigrations restapi && python manage.py migrate restapi && python manage.py makemigrations && python manage.py migrate
# Create media folder
# change your working directory to the top-level directory of the repository and run the following:
$ mkdir -p click_backend/media/profile_pics/
$ wget https://www.personality-insights.com/wp-content/uploads/2017/12/default-profile-pic-e1513291410505.jpg && mv default-profile-pic-e1513291410505.jpg click_backend/media/default.jpeg

# Run server
$ python manage.py runserver
```

If you have applied migrations you would like to delete run the following command:
``` bash
$ rm db.sqlite3 && rm -r restapi/migrations
```