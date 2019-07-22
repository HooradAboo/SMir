import json

import paho.mqtt.client as mqtt
from recognition import FaceRecognition
from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

recognition = FaceRecognition()

in_use = False


def motion_sensor(channel):
    if GPIO.input(21):
        print('detected')
        if recognition.known_face_names and not in_use:
            print(recognition.recognize_from_camera())


def detect_recognize():
    try:
        GPIO.add_event_detect(21, GPIO.RISING, callback=motion_sensor)
        while True:
            sleep(5)
    finally:
        print('interrupt')


def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    if msg.topic == 'camera/signup':
        global in_use
        in_use = True
        recognition.take_picture_and_train(payload)
        print(recognition.recognize_from_camera())
        client.publish(topic="camera/signup/done", payload="ok")
        in_use = False
    if msg.topic == 'user/info':
        print(json.loads(payload))


def on_log(client, userdata, level, buf):
    print("log: ", buf)


client = mqtt.Client()
client.on_message = on_message
client.on_log = on_log
client.connect('192.168.43.144', port=1883)
client.subscribe("camera/signup")
client.subscribe("user/info")
client.loop_start()
detect_recognize()

