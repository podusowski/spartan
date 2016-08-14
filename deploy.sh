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
    sudo -u www-data bash -c 'git pull'
    sudo -u www-data bash -c './manage.py migrate'
    sudo -u www-data bash -c './manage.py collectstatic --noinput'
    service apache2 start
}

function make_virtualenv()
{
    virtualenv -p python3 env
    . env/bin/activate
    pip install -r requirements.txt
}

function help()
{
    grep '^function .*()' $0
}

actions=$@

if [ -z "$actions" ]; then
    # yes, virtualenv is made twice
    actions="print_warning make_virtualenv pull_www make_virtualenv"
fi

for action in $actions; do
    echo "*** $action"
    $action
    echo "***"
done
