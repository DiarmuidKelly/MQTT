FROM eclipse-mosquitto

EXPOSE 1883
EXPOSE 9001

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["sh", "/entrypoint.sh"]
CMD ["/usr/sbin/mosquitto","-c","/mosquitto/config/mosquitto.conf"]