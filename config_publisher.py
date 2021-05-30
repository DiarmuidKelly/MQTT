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

        ret = mqtt_client1.publish(MQTT_CONFIG_TOPIC, "testing")  # publish
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
