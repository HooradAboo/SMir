import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
from recognition import FaceRecognition
import datetime
import json
import sys
from datetime import datetime
from time import sleep
from PyQt5.QtCore import QTimer, Qt, QFile, QTextStream
from PyQt5.QtWidgets import QWidget, QGridLayout, QApplication, QLabel, QPlainTextEdit

# Configuration:
info = {"tasks": [{"tasks": ["Finish Project", ""], "task_list": "My Tasks"}],
        "weather": {"cod": 200, "wind": {"speed": 6.2, "deg": 140}, "dt": 1563779177,
                    "sys": {"sunrise": 1563759255, "sunset": 1563810423, "type": 1, "country": "IR",
                            "message": 0.0085, "id": 7464}, "clouds": {"all": 40}, "id": 112931,
                    "visibility": 10000, "base": "stations", "timezone": 16200, "name": "Tehran",
                    "weather": [{"main": "Clouds", "id": 802, "description": "scattered clouds", "icon": "03d"}],
                    "coord": {"lat": 35.7, "lon": 51.4},
                    "main": {"temp_max": 310.15, "humidity": 12, "temp_min": 310.15, "pressure": 1015,
                             "temp": 310.15}}, "calendar": [{"date": "2019-07-23T15:30:00+04:30", "event": "Kish"},
                                                            {"date": "2019-07-23T15:30:00+04:30", "event": "Kish"},
                                                            {"date": "2019-07-23T15:30:00+04:30", "event": "Kish"}]}
new_notifications = []
temps = [0]
currentDT = datetime.now()
max_history = 10

name = 'Mahtab'

WINDOW_HEIGHT = 1500
WINDOW_WIDTH = 800

TITLE_STYLES = 'margin: 10; font-size: 20px; font-weight: bold;'
EVENT_STYLES = 'margin: 10; font-size: 15px;'

# Initialize GPIOs

GPIO.setmode(GPIO.BCM)

GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

recognition = FaceRecognition()

in_use = False
requested_info = False


class Screen(QWidget):
    def __init__(self):
        super().__init__()

        grid_layout = QGridLayout()
        self.setLayout(grid_layout)

        timer = QTimer(self)
        timer.timeout.connect(self.update_data)
        timer.start(1000)

        self.name_title = QLabel(
            text=name,
            alignment=Qt.AlignCenter,
            styleSheet=TITLE_STYLES,
        )
        grid_layout.addWidget(self.name_title)
        self.clock_log = QLabel(alignment=Qt.AlignCenter,
                                )
        self.clock_log.resize(WINDOW_HEIGHT, WINDOW_WIDTH)
        self.clock_log.setStyleSheet(
            'font-weight: bold; font-size: 20px;'
        );
        grid_layout.addWidget(self.clock_log)

        w_title = QLabel(
            text='Weather:',
            alignment=Qt.AlignLeft,
            styleSheet=EVENT_STYLES,
        )
        grid_layout.addWidget(w_title)

        self.weather_title = QLabel(
            text=info['weather']['weather'][0]['description'],
            alignment=Qt.AlignCenter,
            styleSheet=TITLE_STYLES,
        )
        grid_layout.addWidget(self.weather_title)

        event_title = QLabel(
            text='Upcoming Events:',
            alignment=Qt.AlignLeft,
            styleSheet=EVENT_STYLES,
        )
        grid_layout.addWidget(event_title)

        self.events = QPlainTextEdit(self)
        self.events.resize(WINDOW_HEIGHT, WINDOW_WIDTH)
        self.events.resize(400, 200)
        grid_layout.addWidget(self.events)

        self.temp_title = QLabel(
            text='Real feel:',
            alignment=Qt.AlignLeft,
            styleSheet=EVENT_STYLES,
        )
        grid_layout.addWidget(self.temp_title)
        self.temp_log = QLabel(alignment=Qt.AlignCenter,
                               )
        self.temp_log.resize(WINDOW_HEIGHT, WINDOW_WIDTH)
        self.temp_log.setStyleSheet(
            'font-weight: bold; font-size: 20px'
        );
        grid_layout.addWidget(self.temp_log)

        tasks_title = QLabel(
            text='Upcoming Tasks:',
            alignment=Qt.AlignLeft,
            styleSheet=EVENT_STYLES,
        )
        grid_layout.addWidget(tasks_title)
        self.tasks = QPlainTextEdit(self)
        self.tasks.resize(WINDOW_HEIGHT, WINDOW_WIDTH)
        self.tasks.resize(400, 200)
        grid_layout.addWidget(self.tasks)

        self.setWindowTitle('SMir')

    def update_data(self):
        global counter

        self.temp_log.setText(str(temps[-1]) + ' °C')
        self.name_title.setText(str(name))
        self.weather_title.setText(info['weather']['weather'][0]['description'])
        self.clock_log.setText(str(datetime.now().hour) + ':' + str(datetime.now().minute))
        events = [event for event in info['calendar']]

        if len(events) > 1:
            self.events.setPlainText(
                f'{events[0]["event"]}' + ': ' + f'{events[0]["date"]}'
                '\n'
                f'{events[1]["event"]}' + ': ' + f'{events[1]["date"]}'
            )
        else:
            self.events.setPlainText(
                f'{events[0]["event"]}' + ': ' + f'{events[0]["date"]}'
            )

        self.tasks.setPlainText(
            f'{info["tasks"][0]["task_list"]}' + ': ' + f'{info["tasks"][0]["tasks"][0]}'
        )
        self.update()


def toggle_stylesheet(path):
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("No Qt Application found.")

    file = QFile(path)
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())

    global style
    style = 'dark'


app = QApplication(sys.argv)
toggle_stylesheet('theme/dark.qss')

screen = Screen()
screen.setGeometry(100, 100, 400, 400)


def motion_sensor(channel):
    if GPIO.input(21):
        print('detected')
        global requested_info
        if recognition.known_face_names and not in_use:
            people = recognition.recognize_from_camera()
            if not requested_info and people and 'Unknown' not in people :
                client.publish(topic="user/request_info", payload=people[0])
                requested_info = True


def detect_recognize():
    try:
        GPIO.add_event_detect(21, GPIO.RISING, callback=motion_sensor)
        while True:
            sleep(5)
    finally:
        print('interrupt')


# Setup callback functions that are  called when MQTT events happen like
# connecting to the server or receiving data from a subscribed feed. 
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/pi/notif")
    client.subscribe("/pi/dht")
    client.subscribe("camera/signup")
    client.subscribe("user/info")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    payload = msg.payload.decode("utf-8")
    if msg.topic == '/pi/notif':

        # all notifications from any device are stored here and printed in rpi console.    
        notif_list = msg.split(' ', 1)
        new_notifications.append(msg)

    # DHT & MQ9 send details to the "/pi/dht" topic
    elif msg.topic == '/pi/dht':
        dht_response = msg.payload.decode('UTF-8')
        print(dht_response)
        temps.append(dht_response[0])

    elif msg.topic == 'camera/signup':
        global in_use
        in_use = True
        recognition.take_picture_and_train(payload)
        print(recognition.recognize_from_camera())
        client.publish(topic="camera/signup/done", payload=payload)
        in_use = False

    elif msg.topic == 'user/info':
        global info
        info = json.loads(payload)
        screen.show()


def on_log(client, userdata, level, buf):
    print("log: ", buf)


# Create MQTT client and connect to localhost, i.e. the Raspberry Pi running
# this script and the MQTT server. 
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_log = on_log
client.connect('192.168.43.144', 1883, 60)
# Connect to the MQTT server and process messages in a background thread. 
client.loop_start()
# Main loop to listen for button presses. 
print('Script is running, press Ctrl-C to quit...')

screen.show()
detect_recognize()
sys.exit(app.exec_())
