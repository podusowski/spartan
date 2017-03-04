#!/bin/bash

set -e
set -u

function die() {
    echo $@
    exit 1
}

test `id -u` -eq 0 || die "need to be root"

base=`pwd`
production_dir="/var/www/spartan/"
production_archive="$base/_deploy.tar"
production_user="www-data"
apache_sites_available_dir="/etc/apache2/sites-available/"

test -e $apache_sites_available_dir || die "can't locate apache sites directory"

git archive --output $production_archive HEAD

pushd $production_dir
service apache2 stop

sudo -E -u $production_user bash << EOF
    tar xvf $production_archive
    virtualenv -p python3 env
    source env/bin/activate
    pip install --upgrade -r requirements.txt
    ./manage.py migrate || exit 1
    rm -vrf $production_dir/_files/static
    echo "static"
    ./manage.py collectstatic --noinput
EOF

cp 000-default.conf $apache_sites_available_dir
service apache2 start
popd

rm $production_archive
