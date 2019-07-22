import sys
from random import randint
from datetime import datetime
import time

from PyQt5.QtCore import QTimer, Qt, QFile, QTextStream
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QApplication, \
    QLabel, QPlainTextEdit
from pyqtgraph import PlotWidget, PlotDataItem

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

max_history = 10
max_log = 2
counter = 2
fans = [0 * max_history]  # TODO
temps = [1, 2, 3]
currentDT = datetime.now()
name = 'Mahtab'

WINDOW_HEIGHT = 1500
WINDOW_WIDTH = 800

TITLE_STYLES = 'margin: 10; font-size: 20px; font-weight: bold;'
EVENT_STYLES = 'margin: 10; font-size: 15px;'


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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    toggle_stylesheet('theme/dark.qss')

    screen = Screen()
    screen.setGeometry(100, 100, 400, 400)

    screen.show()

    sys.exit(app.exec_())
