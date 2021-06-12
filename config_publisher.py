#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import threading
import json
import time
import datetime as dt
from influxdb import InfluxDBClient
import configparser
import pathlib

config = configparser.ConfigParser()
config_file = pathlib.Path('./config.ini')
config_section = 'DEFAULT'
config.read(config_file)
config = config[config_section]

MQTT_ADDRESS = config["MQTT_ADDRESS"]
MQTT_USER = config["MQTT_USER"]
MQTT_PASSWORD = config["MQTT_PASSWORD"]
MQTT_TOPIC = config["MQTT_TOPIC"]
MQTT_CONFIG_TOPIC = config["MQTT_CONFIG_TOPIC"]

db_client = InfluxDBClient(host=config['InfluxDB_HOST'], port=config['InfluxDB_PORT'], username=config['InfluxDB_USER'], password=config['InfluxDB_PASSWORD'],
                           database=config['InfluxDB_DATABASE'])

override_central_time = True


def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))


def on_publish(client, userdata, result):
    """create function for callback"""
    print("data published")
    pass


def main():
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.connect(MQTT_ADDRESS, 1883, 60)


def pubber():
    while True:
        mqtt_client1 = mqtt.Client()
        mqtt_client1.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        mqtt_client1.connect(MQTT_ADDRESS, 1883)
        mqtt_client1.on_publish = on_publish  # assign function to callback

        # ret = mqtt_client1.publish(MQTT_CONFIG_TOPIC, "testing")  # publish
        utc_dt = dt.datetime.now(dt.timezone.utc)  # UTC time
        dtime = utc_dt.astimezone()  # local time
        json_body = {
                "measurement": "h-pi-1",
                "tags": {
                    "host": "h-pi",
                    "region": "eu-centre",
                },
                "time": str(dtime),
                "fields": {
                    "AT1": 3300,
                    "AT2": 3200,
                    "AT3": 2800,
                    "LT1": 1200,
                    "LT2": 1000,
                    "LT3": 1000,
                    "PD1": 10000,
                    "PD2": 10000,
                    "PD3": 2000,
                    "PD4": 4000,
                    "PTO": 600,
                    "PTV": 60,
                    "UF": 10000000,
                    "Pump_on": 0
                }
            }

        json_body = json.dumps(json_body, indent=4)
        ret = mqtt_client1.publish(MQTT_CONFIG_TOPIC, json_body)  # publish
        print(ret)
        time.sleep(5)


if __name__ == '__main__':
    print('MQTT to InfluxDB bridge')
    print(db_client.get_list_database())
    db_client.switch_database('apartment')
    # query = 'select heat_index from esp32_apartment_1;'
    # result = db_client.query(query)
    # print(result)
    m = threading.Thread(target=pubber)
    m.start()
    # TODO: record all MQTT recordings to object for Mongo insert
