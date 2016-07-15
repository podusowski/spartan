if [ `id -u` -ne 0 ]; then
    echo you should be root to do this
    exit 1
fi

echo make sure what that script is doing before continuing
echo hit enter or ^c to abort

read line

if ! pwd | grep '/var/www'; then
    echo 'it seems you are outside apache directory (at least as far as I can say), hit enter if you are sure if this is the right place'
    read line
fi

service apache2 stop
sudo -u www-data bash -c 'git pull'
sudo -u www-data bash -c './manage.py migrate'
service apache2 start
