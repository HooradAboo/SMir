import json

import paho.mqtt.client as mqtt


def on_message(client, userdata, msg):
    if msg.topic == 'user/info':
        data = json.loads(msg.payload)
        print(data)


def on_log(client, userdata, level, buf):
    print("log: ", buf)


client = mqtt.Client()
client.on_message = on_message
client.on_log = on_log
client.connect('iot.eclipse.org', port=1883)
client.subscribe("user/info")
client.subscribe("user/pictures")
