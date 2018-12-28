#!/bin/bash

set -e

python manage.py migrate
gunicorn --bind 0.0.0.0:8000 --worker-class=gevent spartan.wsgi
