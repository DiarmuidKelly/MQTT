#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import json
import time
import os, sys
import datetime as dt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from config.config import parse
import logging
import threading

logging.basicConfig(format='%(asctime)s -- %(levelname)s :  %(funcName)s(ln:%(lineno)d) :: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def on_connect(client, userdata, flags, reason_code, properties):
    """ The callback for when the client receives a CONNACK response from the server."""
    logger.debug('Connected with result code ' + str(reason_code))
    pass

def on_publish(client, userdata, mid, reason_code, properties):
    """create function for callback"""
    logger.debug("data published")
    pass

def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    logger.debug(msg.topic + ' ' + str(msg.payload))
    my_json = msg.payload.decode('utf8').replace("'", '"')
    if str(msg.topic).split("/")[0] == 'config':
        logger.info("Config message received")
        return
    logger.info("Message received")
    data = json.loads(my_json)
    s = json.dumps(data, indent=4, sort_keys=True)
    s = json.loads(s)
    utc_dt = dt.datetime.now(dt.timezone.utc)
    dtime = utc_dt.astimezone()

    json_body = {
            "measurement": s['measurement'],
            "tags": s['tags'],
            "fields": s['fields'],
            "time": str(dtime)
        }
    write_api.write(bucket=bucket, record=Point.from_dict(json_body))

def main():
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "mqtt-listener")
    mqtt_client.username_pw_set(config["MQTT_USER"], config["MQTT_PASSWORD"])
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(config["MQTT_ADDRESS"], 1883, 60)
    mqtt_client.subscribe(config["MQTT_TOPIC"])
    # mqtt_client.subscribe(config["MQTT_CONFIG_TOPIC"])
    mqtt_client.loop_forever()


def pubber():
    mqtt_client1 = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "mqtt-publisher")
    mqtt_client1.username_pw_set(config["MQTT_USER"], config["MQTT_PASSWORD"])
    mqtt_client1.connect(config["MQTT_ADDRESS"], 1883)

    mqtt_client1.on_publish = on_publish

    while True:
        json_body = {
                "measurement": "test",
                "tags": {"test": "test"},
                "fields": {"test": 1},
            }        

        json_body = json.dumps(json_body, indent=4)
        mqtt_client1.publish(config["MQTT_CONFIG_TOPIC"], json_body)
        time.sleep(5)

if __name__ == '__main__':
    logger.info('MQTT to InfluxDB bridge')
    config = parse(config_section="TEST")

    m = threading.Thread(target=pubber, daemon=True)
    m.start()

    bucket = "main"
    db_client = InfluxDBClient(url=f"http://{config['InfluxDB_HOST']}:{config['InfluxDB_PORT']}", 
                                token= config['INFLUXDB_TOKEN'], 
                                org=config['INFLUXDB_ORG'])
    write_api = db_client.write_api(write_options=SYNCHRONOUS)
    query_api = db_client.query_api()

    try:
        main()
    except KeyboardInterrupt:
        logger.warning("Stopping")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

