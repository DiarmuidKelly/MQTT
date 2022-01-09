#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import json
import datetime as dt
from influxdb import InfluxDBClient
from config.config import parse
import logging

logging.basicConfig(format='%(asctime)s -- %(levelname)s:%(message)s', level=logging.DEBUG)

def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    logging.debug('Connected with result code ' + str(rc))
    client.subscribe(config["MQTT_TOPIC"])


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    logging.info(msg.topic + ' ' + str(msg.payload))
    my_json = msg.payload.decode('utf8').replace("'", '"')
    if str(msg.topic).split("/")[-1] == 'config':
        return
    data = json.loads(my_json)
    s = json.dumps(data, indent=4, sort_keys=True)
    s = json.loads(s)
    utc_dt = dt.datetime.now(dt.timezone.utc)  # UTC time
    dtime = utc_dt.astimezone()  # local time

    if override_central_time:
        json_body = [
           {
               "measurement": s['measurement'],
               "tags": s['tags'],
               "time": str(dtime),
               "fields": s['fields']
           }
        ]
    db_client.write_points(json_body)

def main():
    override_central_time = True
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(config["MQTT_USER"], config["MQTT_PASSWORD"])
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(config["MQTT_ADDRESS"], 1883, 60)
    mqtt_client.loop_forever()

if __name__ == '__main__':
    logging.info('MQTT to InfluxDB bridge')
    config = parse(config_section="TEST")
    db_client = InfluxDBClient(host=config['InfluxDB_HOST'], 
                                port=config['InfluxDB_PORT'], 
                                username=config['InfluxDB_USER'], 
                                password=config['InfluxDB_PASSWORD'],
                                database=config['InfluxDB_DATABASE'])
    
    logging.debug(db_client.get_list_database())
    db_client.switch_database('apartment')
    main()
