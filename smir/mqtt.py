import paho.mqtt.client as mqtt


def on_log(client, userdata, level, buf):
    print("log: ", buf)


client = mqtt.Client()
client.on_log = on_log
client.connect("127.0.0.1", 1883, 60)

