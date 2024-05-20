#!/bin/sh

RAWPASSWDFILE=/etc/mosquitto/passwd.raw
OUTPASSWDFILE=/etc/mosquitto/passwd

if [ -f $RAWPASSWDFILE ]; then
    echo "converting password file"
    cp -i $RAWPASSWDFILE $OUTPASSWDFILE
    mosquitto_passwd -U $OUTPASSWDFILE
fi

exec "$@"