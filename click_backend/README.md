# Backend

Setup the virtual environment and install dependencies:

```bash
# Change your working directory to the current directory of the repository and run the following commands:
$ python -m venv ./venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

Start app:

```bash
# Create database
$ python manage.py makemigrations && python manage.py migrate
# Create media folder
$ mkdir -p media/profile_pics/
$ wget https://www.personality-insights.com/wp-content/uploads/2017/12/default-profile-pic-e1513291410505.jpg && mv default-profile-pic-e1513291410505.jpg media/default.jpeg

# Run server
$ python manage.py runserver
```

If you have applied migrations you would like to delete, run the following command:

```bash
$ rm db.sqlite3 && rm -r restapi/migrations
```
