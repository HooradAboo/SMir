import paho.mqtt.client as mqtt


def on_connect(client, userdata, rc):
    client.subscribe("$SYS/#")


def on_message(client, userdata, msg):
    # Do something
    pass


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("iot.eclipse.org", 1883, 60)
