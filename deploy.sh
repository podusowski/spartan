#!/bin/bash

function expect_root()
{
    if [ `id -u` -ne 0 ]; then
        echo you should be root to do this
        exit 1
    fi
}

function print_warning()
{
    echo make sure what that script is doing before continuing
    echo hit enter or ^c to abort
    read line
}

function expect_www_wd()
{
    if ! pwd | grep '/var/www'; then
        echo 'it seems you are outside apache directory (at least as far as I can say), hit enter if you are sure if this is the right place'
        read line
    fi
}

function pull_www()
{
    expect_root
    expect_www_wd

    service apache2 stop
    sudo -E -u www-data bash -c ". env/bin/activate && git pull && ./manage.py migrate && ./manage.py collectstatic --noinput"
#    sudo -E -u www-data bash -c './manage.py migrate'
#    sudo -E -u www-data bash -c './manage.py collectstatic --noinput'
    service apache2 start
}

function update_virtualenv()
{
    pip install -r requirements.txt
}

function help()
{
    grep '^function .*()' $0
}

# this wont work inside a function
. env/bin/activate

actions=$@

if [ -z "$actions" ]; then
    actions="print_warning pull_www update_virtualenv"
fi

for action in $actions; do
    echo "*** $action"
    $action
    echo "***"
done
