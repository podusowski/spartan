# spartan
Web activity tracker for strength and cardio (GPS tracked) activities.

# required dependencies
  virtualenv
  postgresql-server-dev-all
  build-essential
  python3-dev

# first time running preparations
  virtualenv -p python3 env

# how to run
  . env/bin/activate
  pip install -r requirements.txt
  ./manage.py migrate
  ./manage.py collectstatic

# running tests
  ./manage.py tests

# running server
  ./manage.py runserver


<a href="https://travis-ci.org/podusowski/spartan"><img src="https://travis-ci.org/podusowski/spartan.svg?branch=master" /></a>
<a href="https://codecov.io/gh/podusowski/spartan"><img src="https://codecov.io/gh/podusowski/spartan/branch/master/graph/badge.svg" alt="Codecov" /></a>
