# RPi  code
import time
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import threading
import Adafruit_DHT
import pandas as pd
import numpy as np
import datetime

import sys
from random import randint
from datetime import datetime

from PyQt5.QtCore import QTimer, Qt, QFile, QTextStream
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QApplication, \
    QLabel, QPlainTextEdit
from pyqtgraph import PlotWidget, PlotDataItem

# Configuration:
calendar = {"tasks": [{"tasks": ["Finish Project", ""], "task_list": "My Tasks"}],
            "weather": {"cod": 200, "wind": {"speed": 6.2, "deg": 140}, "dt": 1563779177,
                        "sys": {"sunrise": 1563759255, "sunset": 1563810423, "type": 1, "country": "IR",
                                "message": 0.0085, "id": 7464}, "clouds": {"all": 40}, "id": 112931,
                        "visibility": 10000, "base": "stations", "timezone": 16200, "name": "Tehran",
                        "weather": [{"main": "Clouds", "id": 802, "description": "scattered clouds", "icon": "03d"}],
                        "coord": {"lat": 35.7, "lon": 51.4},
                        "main": {"temp_max": 310.15, "humidity": 12, "temp_min": 310.15, "pressure": 1015,
                                 "temp": 310.15}}, "calendar": [{"date": "2019-07-23T15:30:00+04:30", "event": "Kish"}]}
new_notifications = []
temps = []

max_history = 10
max_log = 2
counter = 2
fans = [0 * max_history]  # TODO

style = 'light'

WINDOW_HEIGHT = 640
WINDOW_WIDTH = 480
TITLE_STYLES = 'margin: 10; font-size: 20px; font-weight: bold;'

# Initialize GPIOs

GPIO.setmode(GPIO.BCM)


def ask_for_temp_feddback():
    client.publish('/esp3/dht_mq9', 'feedback')


# Setup callback functions that are  called when MQTT events happen like 
# connecting to the server or receiving data from a subscribed feed. 
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/pi/notif")
    client.subscribe("/pi/dht")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    date = datetime.datetime.now()

    print(msg.topic + " " + str(msg.payload))

    if msg.topic == '/pi/notif':

        # all notifications from any device are stored here and printed in rpi console.    
        notif_list = msg.split(' ', 1)
        new_notifications.append(msg)

    # DHT & MQ9 send details to the "/pi/dht" topic
    elif msg.topic == '/pi/dht':
        dht_response = msg.payload.decode('UTF-8')
        print(dht_response)
        temp = dht_response[]  # TODO add response


class Screen(QWidget):
    def __init__(self):
        super().__init__()

        grid_layout = QGridLayout()
        self.setLayout(grid_layout)

        timer = QTimer(self)
        timer.timeout.connect(self.update_data)
        timer.start(1000)

        temp_title = QLabel(
            text='ُTemperature:',
            alignment=Qt.AlignCenter,
            styleSheet=TITLE_STYLES,
        )
        grid_layout.addWidget(temp_title)
        self.temp_data = PlotDataItem(temps)
        temp_widget = PlotWidget()
        temp_widget.addItem(self.temp_data)
        temp_widget.setXRange(0, max_history)
        temp_widget.setYRange(-10, 60)
        grid_layout.addWidget(temp_widget)

        fan_title = QLabel(
            text='Fan',
            alignment=Qt.AlignCenter,
            styleSheet=TITLE_STYLES,
        )
        grid_layout.addWidget(fan_title)
        self.fan_data = PlotDataItem(fans)
        fan_widget = PlotWidget()
        fan_widget.addItem(self.fan_data)
        fan_widget.setXRange(0, max_history)
        fan_widget.setYRange(0, 100)
        grid_layout.addWidget(fan_widget)

        last_log_title = QLabel(
            text='Latest Event',
            alignment=Qt.AlignCenter,
            styleSheet=TITLE_STYLES,
        )
        grid_layout.addWidget(last_log_title)
        self.last_log = QLabel()
        self.last_log.resize(WINDOW_HEIGHT, WINDOW_WIDTH)
        self.last_log.setStyleSheet(
            'font-weight: bold;'
            'background-color: grey;'
        );
        grid_layout.addWidget(self.last_log)

        logs_title = QLabel(
            text='Event History',
            alignment=Qt.AlignCenter,
            styleSheet=TITLE_STYLES,
        )
        grid_layout.addWidget(logs_title)
        self.logs = QPlainTextEdit(self)
        self.logs.resize(WINDOW_HEIGHT, WINDOW_WIDTH)
        self.logs.resize(400, 200)
        grid_layout.addWidget(self.logs)

        self.setWindowTitle('Screen')

    def update_data(self):
        global counter

        # Fixme:  Foo data
        temps.append(counter)
        fans.append(counter)
        new_log = f'Event {counter} happend'

        counter += randint(-5, 10)
        self.temp_data.setData(temps[-max_history:])
        self.fan_data.setData(fans[-max_history:])

        if new_log:
            date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            date_log = f'{date_time}: {new_log}'
            self.logs.setPlainText(
                f'{self.last_log.text()}'
                '\n'
                f'{self.logs.toPlainText()}'
            )
            self.last_log.setText(date_log)

        self.update()


# Create MQTT client and connect to localhost, i.e. the Raspberry Pi running
# this script and the MQTT server. 
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect('localhost', 1883, 60)
# Connect to the MQTT server and process messages in a background thread. 
client.loop_start()
# Main loop to listen for button presses. 
print('Script is running, press Ctrl-C to quit...')

## screen
app = QApplication(sys.argv)
screen = Screen()
screen.setGeometry(100, 100, 400, 400)

screen.show()

sys.exit(app.exec_())
