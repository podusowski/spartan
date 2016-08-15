#!/bin/bash

# asserts
if [ `id -u` -ne 0 ]; then
    echo you should be root to do this
    exit 1
fi

if ! pwd | grep '/var/www'; then
    echo "it seems you are outside apache directory"
    exit 1
fi

apt-get install apache2 supervisor

service apache2 stop

if [ ! -e env ]; then
    virtualenv env
fi

. env/bin/activate

sudo -E -u www-data bash -c ". env/bin/activate &&\
                             git pull &&\
                             ./manage.py migrate &&\
                             rm static/ -rf &&\
                             ./manage.py collectstatic --noinput"

cp 000-default.conf /etc/apache2/sites-available/
pip install -r requirements.txt

service apache2 start
