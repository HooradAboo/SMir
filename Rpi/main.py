import SMir

import sys
from random import randint
from datetime import datetime

from PyQt5.QtCore import QTimer, Qt, QFile, QTextStream
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QApplication, \
    QLabel, QPlainTextEdit
from pyqtgraph import PlotWidget, PlotDataItem

calendar = {"tasks": [{"tasks": ["Finish Project", ""], "task_list": "My Tasks"}],
            "weather": {"cod": 200, "wind": {"speed": 6.2, "deg": 140}, "dt": 1563779177,
                        "sys": {"sunrise": 1563759255, "sunset": 1563810423, "type": 1, "country": "IR",
                                "message": 0.0085, "id": 7464}, "clouds": {"all": 40}, "id": 112931,
                        "visibility": 10000, "base": "stations", "timezone": 16200, "name": "Tehran",
                        "weather": [{"main": "Clouds", "id": 802, "description": "scattered clouds", "icon": "03d"}],
                        "coord": {"lat": 35.7, "lon": 51.4},
                        "main": {"temp_max": 310.15, "humidity": 12, "temp_min": 310.15, "pressure": 1015,
                                 "temp": 310.15}}, "calendar": [{"date": "2019-07-23T15:30:00+04:30", "event": "Kish"}]}

max_history = 10
max_log = 2
counter = 2
temps = [0 * max_history]  # TODO
fans = [0 * max_history]  # TODO

style = 'light'

WINDOW_HEIGHT = 640
WINDOW_WIDTH = 480

TITLE_STYLES = 'margin: 10; font-size: 20px; font-weight: bold;'


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


def toggle_stylesheet(path):
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("No Qt Application found.")

    file = QFile(path)
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())

    global style
    style = 'dark' if style == 'light' else 'light'


if __name__ == '__main__':
    app = QApplication(sys.argv)
    toggle_stylesheet('theme/light.qss')

    screen = Screen()
    screen.setGeometry(100, 100, 400, 400)

    dark_btn = QPushButton('Light/Dark', screen)
    dark_btn.clicked.connect(
        lambda: toggle_stylesheet(
            'theme/dark.qss' if style == 'light' else 'theme/light.qss'
        )
    )

    screen.show()

    sys.exit(app.exec_())
