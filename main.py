#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import threading
import json
import time
import datetime as dt
from influxdb import InfluxDBClient

MQTT_ADDRESS = 'raspberrypi.local'
MQTT_USER = 'client'
MQTT_PASSWORD = 'server'
MQTT_TOPIC = 'apartment/+/+'

db_client = InfluxDBClient(host='192.168.178.50', port=8086, username='grafana', password='grafana',
                           database="apartment")


def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    print(msg.topic + ' ' + str(msg.payload))
    my_json = msg.payload.decode('utf8').replace("'", '"')
    # print(my_json)
    data = json.loads(my_json)
    s = json.dumps(data, indent=4, sort_keys=True)
    print(s)
    utc_dt = dt.datetime.now(dt.timezone.utc) # UTC time
    dtime = utc_dt.astimezone() # local time

    json_body = [
        {
            "measurement": "esp32_apartment_1",
            "tags": {
                "host": "esp32-1",
                "region": "eu-centre"
            },
            "time": dtime,
            "fields": {
                "heat_index": data['heat_i'],
                "humidity": data['humidity'],
                "light": data['light'],
                "temp": float(data['temp'])
            }
        }
    ]
    db_client.write_points(json_body)


def on_publish(client, userdata, result):
    """create function for callback"""
    print("data published")
    pass


def main():
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_ADDRESS, 1883)
    mqtt_client.loop_forever()


def pubber():
    while True:
        mqtt_client1 = mqtt.Client()
        mqtt_client1.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        mqtt_client1.connect(MQTT_ADDRESS, 1883)
        mqtt_client1.on_publish = on_publish  # assign function to callback

        ret = mqtt_client1.publish("home/livingroom/bulb1", "on")  # publish
        print(ret)
        time.sleep(5)


if __name__ == '__main__':
    # x = threading.Thread(target=pubber)
    # x.start()


    print('MQTT to InfluxDB bridge')
    print(db_client.get_list_database())
    db_client.switch_database('apartment')
    # query = 'select heat_index from esp32_apartment_1;'
    # result = db_client.query(query)
    # print(result)
    main()
    # TODO: record all MQTT recordings to object for Mongo insert
