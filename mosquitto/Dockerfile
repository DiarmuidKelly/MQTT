FROM eclipse-mosquitto

EXPOSE 1883

COPY passwd /etc/mosquitto/passwd
COPY mosquitto.conf /mosquitto/config/mosquitto.conf

RUN mosquitto_passwd -U /etc/mosquitto/passwd
# COPY entrypoint.sh /entrypoint.sh
# ENTRYPOINT ["sh", "/entrypoint.sh"]
CMD ["/usr/sbin/mosquitto","-c","/mosquitto/config/mosquitto.conf"]