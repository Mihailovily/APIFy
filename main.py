import sys
from io import BytesIO

import requests
from PIL import Image, ImageQt
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton

SCREEN_SIZE = [600, 480]


# Эйфелева башня
# 48.858215, 2.294348


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.lat = 0  # широта
        self.lng = 0  # долгота
        self.MapScale = 0.002
        self.initUI()

    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key_PageUp, QtCore.Qt.Key_PageDown, QtCore.Qt.Key_Right, QtCore.Qt.Key_Left,
                           QtCore.Qt.Key_Up, QtCore.Qt.Key_Down] and self.lng and self.lat:
            if event.key() == QtCore.Qt.Key_PageUp:
                self.MapScale -= 0.0008
                if self.MapScale < 0:
                    self.MapScale = 0
            elif event.key() == QtCore.Qt.Key_PageDown:  # Key_PageUp:
                self.MapScale += 0.0008
                if self.MapScale > 17:
                    self.MapScale = 17
            if event.key() == QtCore.Qt.Key_Right:
                self.lng += 0.0002
            if event.key() == QtCore.Qt.Key_Left:
                self.lng -= 0.0002
            if event.key() == QtCore.Qt.Key_Up:
                self.lat += 0.0002
            if event.key() == QtCore.Qt.Key_Down:
                self.lat -= 0.0002

            self.remap()

    def getImage(self):
        map_request = f"http://static-maps.yandex.ru/1.x/?ll=" \
                      f"{str(self.lng)},{str(self.lat)}&spn={self.MapScale},{self.MapScale}&l=map"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.img = ImageQt.ImageQt(Image.open(BytesIO(response.content)))

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        self.name_label = QLabel(self)
        self.name_label.setText("Введите координаты: ")
        self.name_label.setFont(QFont("Roboto", 13, QFont.Bold))
        self.name_label.move(0, 5)

        self.coords = QLineEdit(self)
        #self.coords.setText("48.858215, 2.294348")
        self.coords.resize(185, 20)
        self.coords.move(215, 5)

        self.input_coords = QPushButton("Ввести", self)
        self.input_coords.resize(self.input_coords.sizeHint())
        self.input_coords.move(410, 4)
        self.input_coords.clicked.connect(self.redraw)

        self.reset = QPushButton("Сбросить", self)
        self.reset.resize(self.reset.sizeHint())
        self.reset.move(510, 4)
        self.reset.clicked.connect(self.reset_map)

        self.image = QLabel(self)
        self.image.move(0, 30)
        self.image.resize(600, 450)

    def redraw(self):
        self.lat = float(self.coords.text().split(", ")[0])
        self.lng = float(self.coords.text().split(", ")[1])
        self.coords.setEnabled(False)
        self.input_coords.setEnabled(False)
        self.remap()

    def reset_map(self):
        self.coords.setEnabled(True)
        self.input_coords.setEnabled(True)
        self.coords.setText("")
        self.lat = 0  # широта
        self.lng = 0  # долгота
        self.MapScale = 0.002
        self.remap()

    def remap(self):
        self.getImage()
        self.image.setPixmap(QPixmap.fromImage(self.img))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
