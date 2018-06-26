Spartan
-------
Personal activity tracker for both strength and cardio (GPS tracked) excercises.

Live version: http://91.203.132.230 (I couldn't find any cool domain, sorry :))

<a href="https://travis-ci.org/podusowski/spartan"><img src="https://travis-ci.org/podusowski/spartan.svg?branch=master" /></a>
<a href="https://codeclimate.com/github/podusowski/spartan"><img src="https://codeclimate.com/github/podusowski/spartan/badges/gpa.svg" /></a>

<img src="screenshots/dashboard.png?raw=true" />
<img src="screenshots/gps_workout.png?raw=true" />
<img src="screenshots/strength_workout.png?raw=true" />


Deployment and development
==========================
Spartan is built into single `Docker` image which serve the application and static files on port `8000`. There is also a `Makefile` for common tasks so you won't need to remember all those docker parameters. Obviously you need to have [Docker](https://www.docker.com/) installed. On newest Ubuntu you can do this through `sudo apt install docker.io`.


### Tests
Spartan has two level of testing. Unit tests lives near application modules, eg `training/tests/test_hexagons.py` while higher level testing are in global `tests` directory.

All of them are managed by `pytest` which is integrated with `django`. The easiest way to run them is to use `make test` as it will handle all docker stuff.


### How to run locally
You can start debug server using `make debugserver`. It will run the same docker image that is used in production but with `DEBUG` environment variable passed into the container. `DEBUG` will change some things.

- Python logger is set to debug level
- SQLite is used as database, `db.sqlite3` will be created in current directory

After starting, application will be available on port `8000`.


### Deployment
Spartan image doesn't come with the database (except the SQLite which is used only in DEBUG mode) so you have to install it manually (on your host OS or by using docker aswell - docker-compose might be usefull in this case).

When you have your database ready, you can pass its configuration though environment variables: `DB_ENGINE DB_NAME DB_USER DB_PASSWORD DB_HOST`. You can check [`django` documentation](https://docs.djangoproject.com/en/2.0/ref/settings/#databases) to find out what to put in here.

When you have those covered, you can start the container and leave the management to Docker by using `--restart always` flag to `run` command. This way, the container will be running on your machine all the time.

At this point, you database is most likely empty so before using the application, you have to migrate the models.

[TODO]
