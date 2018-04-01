Spartan
-------
Personal activity tracker for both strength and cardio (GPS tracked) excercises.

Live version: http://91.203.132.230 (I couldn't find any cool domain, sorry :))

<a href="https://travis-ci.org/podusowski/spartan"><img src="https://travis-ci.org/podusowski/spartan.svg?branch=master" /></a>
[![Coverage Status](https://coveralls.io/repos/github/podusowski/spartan/badge.svg?branch=master)](https://coveralls.io/github/podusowski/spartan?branch=master)
<a href="https://codeclimate.com/github/podusowski/spartan"><img src="https://codeclimate.com/github/podusowski/spartan/badges/gpa.svg" /></a>

<img src="screenshots/dashboard.png?raw=true" />
<img src="screenshots/gps_workout.png?raw=true" />
<img src="screenshots/strength_workout.png?raw=true" />


Deployment and development
==========================
Spartan is built into single `Docker` image which serve the application and static files on port `8000`. There is also a `Makefile` for common tasks.


### Tests
Spartan has two level of testing. Unit tests lives near application modules, eg `training/tests/test_hexagons.py` while higher level testing are in global `tests` directory.

All of them are managed by `pytest` which is integrated with `django`. The easiest way to run them is to use `make test` as it will handle all docker stuff.


### How to run locally

