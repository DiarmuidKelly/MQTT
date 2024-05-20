#!/bin/sh

RAWPASSWDFILE=/etc/mosquitto/passwd.raw
OUTPASSWDFILE=/etc/mosquitto/passwd

if [ -f $RAWPASSWDFILE ]; then
    echo "converting password file"
    cp -rf $RAWPASSWDFILE $OUTPASSWDFILE
    chmod 0700 $OUTPASSWDFILE
    mosquitto_passwd -U $OUTPASSWDFILE
fi

exec "$@"