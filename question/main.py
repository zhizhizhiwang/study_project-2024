import sys
from PyQt6 import QtCore, QtWidgets, QtGui


class HomeWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()  # 调用父类的__init__
        self.setWindowTitle("Home Page")


