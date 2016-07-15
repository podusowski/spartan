if [ `id -u` -ne 0 ]; then
    echo you should be root to do this
    exit 1
fi

echo you are about to pull changes from git, apply migrations and restart apache server, make sure you know exactly what that script is doing before continuing
echo hit enter or ^c to abort

read line

if ! pwd | grep '/var/www'; then
    echo 'it seems you are outside apache directory (at least as far as I can say), hit enter if you are sure if this is the right place'
    read line
fi

sudo -u www-data bash -c 'service apache stop && git pull && ./manage migrate && service apache start'
