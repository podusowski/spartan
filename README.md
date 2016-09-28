# spartan
Web activity tracker for both strength and cardio (GPS tracked) activities.

<a href="https://travis-ci.org/podusowski/spartan"><img src="https://travis-ci.org/podusowski/spartan.svg?branch=master" /></a>
<a href="https://codecov.io/gh/podusowski/spartan"><img src="https://codecov.io/gh/podusowski/spartan/branch/master/graph/badge.svg" alt="Codecov" /></a>

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
