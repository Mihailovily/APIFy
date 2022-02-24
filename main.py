import sys
from io import BytesIO

import requests
from PIL import Image, ImageQt
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton

SCREEN_SIZE = [600, 520]


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
                           QtCore.Qt.Key_Up, QtCore.Qt.Key_Down, QtCore.Qt.Key_C, 1057] and self.lng and self.lat:
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
            if event.key() in (QtCore.Qt.Key_C, 1057):
                self.reset_map()

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
        self.name_label.move(5, 4)

        self.error_text = QLabel(self)
        self.error_text.setText("                 ")
        self.error_text.setStyleSheet("color: red")
        self.error_text.setFont(QFont("Roboto", 13))
        self.error_text.move(505, 30)

        self.coords = QLineEdit(self)
        self.coords.setText("48.858215, 2.294348")
        self.coords.resize(185, 20)
        self.coords.move(215, 5)

        self.address_text = QLineEdit(self)
        self.address_text.setText("Париж, Эйфелева башня")
        self.address_text.resize(395, 20)
        self.address_text.move(5, 35)

        self.input_coords = QPushButton("Ввести", self)
        self.input_coords.resize(self.input_coords.sizeHint())
        self.input_coords.move(410, 4)
        self.input_coords.clicked.connect(self.redraw)

        self.input_address = QPushButton("Ввести", self)
        self.input_address.resize(self.input_coords.sizeHint())
        self.input_address.move(410, 33)
        self.input_address.clicked.connect(self.search_address)

        self.reset_text = QLabel('"C" для сброса', self)
        self.reset_text.setFont(QFont("Arial", 10, QFont.Bold))
        self.reset_text.move(495, 15)

        self.image = QLabel(self)
        self.image.move(0, 70)
        self.image.resize(600, 450)

    def redraw(self):
        self.lat = float(self.coords.text().split(", ")[0])
        self.lng = float(self.coords.text().split(", ")[1])
        self.block_inputs()
        self.error_text.setText("                 ")
        self.remap()

    def block_inputs(self):
        self.coords.setEnabled(False)
        self.input_coords.setEnabled(False)
        self.input_address.setEnabled(False)
        self.address_text.setEnabled(False)

    def reset_map(self):
        self.coords.setEnabled(True)
        self.input_coords.setEnabled(True)
        self.input_address.setEnabled(True)
        self.address_text.setEnabled(True)
        self.coords.setText("48.858215, 2.294348")
        self.lat = 0  # широта
        self.lng = 0  # долгота
        self.MapScale = 0.002
        self.remap()

    def remap(self):
        self.getImage()
        self.image.setPixmap(QPixmap.fromImage(self.img))

    def search_address(self):
        response = requests.get(
            "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode="
            + self.address_text.text() + "&format=json")
        json_response = response.json()
        if json_response["response"]["GeoObjectCollection"]["featureMember"]:
            # Запрос успешно выполнен, печатаем полученные данные.
            print(json_response)
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            # Полный адрес топонима:
            toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
            # Координаты центра топонима:
            toponym_coodrinates = toponym["Point"]["pos"]
            # Печатаем извлечённые из ответа поля:
            print(toponym_address, "имеет координаты:", toponym_coodrinates)
            self.lat = float(toponym_coodrinates.split()[1])
            self.lng = float(toponym_coodrinates.split()[0])
            self.block_inputs()
            self.error_text.setText("                 ")
            self.remap()
        else:
            # Произошла ошибка выполнения запроса. Обрабатываем http-статус.
            print("Ошибка выполнения запроса")
            self.error_text.setText("Ошибочка!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
