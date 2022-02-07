import sys
from io import BytesIO

import requests
from PIL import Image, ImageQt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton

SCREEN_SIZE = [600, 480]


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.lat = 0  # широта
        self.lng = 0  # долгота
        #self.getImage()
        self.initUI()


    def getImage(self):
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={self.lng},{self.lat}&spn=0.002,0.002&l=map"
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


        # self.label = QLabel(self)
        # self.label.setText("Привет, неопознанный лев")
        # self.label.move(40, 30)

        self.name_label = QLabel(self)
        self.name_label.setText("Введите координаты: ")
        self.name_label.setFont(QFont("Roboto", 13, QFont.Bold))
        self.name_label.move(0, 5)

        self.coords = QLineEdit(self)
        self.coords.resize(285, 20)
        self.coords.move(215, 5)

        self.btn = QPushButton("Ввести", self)
        self.btn.resize(self.btn.sizeHint())
        self.btn.move(510, 4)
        self.btn.clicked.connect(self.redraw)

        ## Изображение
        self.image = QLabel(self)
        self.image.move(0, 30)
        self.image.resize(600, 450)

    def redraw(self):
        self.lat = self.coords.text().split(", ")[0]
        self.lng = self.coords.text().split(", ")[1]
        self.getImage()
        self.image.setPixmap(QPixmap.fromImage(self.img))



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
