# spartan
Web activity tracker for both strength and cardio (GPS tracked) activities.

[http://91.203.132.230] (I couldn't find any cool domain, sorry :))

<a href="https://travis-ci.org/podusowski/spartan"><img src="https://travis-ci.org/podusowski/spartan.svg?branch=master" /></a>
<a href="https://codecov.io/gh/podusowski/spartan"><img src="https://codecov.io/gh/podusowski/spartan/branch/master/graph/badge.svg" alt="Codecov" /></a>
<a href="https://codeclimate.com/github/podusowski/spartan"><img src="https://codeclimate.com/github/podusowski/spartan/badges/gpa.svg" /></a>

<img src="screenshots/dashboard.png?raw=true" />
<img src="screenshots/gps_workout.png?raw=true" />
<img src="screenshots/strength_workout.png?raw=true" />

## How to run locally

### Preparations
This will install required dependencies and create virtual python environment in your working copy. This needs to be done only once after you clone the repo.
```
sudo apt-get install virtualenv postgresql-server-dev-all build-essential python3-dev
virtualenv -p python3 env
```

### Things to do after pulling changes
```
. env/bin/activate
pip install -r requirements.txt
./manage.py migrate
./manage.py collectstatic
```

### Running tests
```
./manage.py test
```

### Running server
```
./manage.py runserver
```
