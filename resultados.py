import sys
import cv2
import random
from pyzbar.pyzbar import decode
import pyrebase
import time
import os
import pygame
from pygame.locals import *
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ResultWindow(QtWidgets.QWidget):
    update_gif = QtCore.pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def setupUi(self, Form):
        Form.setObjectName("ResultWindow")
        Form.resize(1920, 1000)

        self.back_result = QtWidgets.QLabel(Form)
        self.back_result.setGeometry(QtCore.QRect(0, 0, 1920, 1000))
        self.movie = QtGui.QMovie("RoboInges_result.gif")
        self.back_result.setMovie(self.movie)
        self.movie.start()

        self.result_text = QtWidgets.QLabel(Form)
        self.result_text.setGeometry(QtCore.QRect(450, 300, 1100, 700))
        self.result_text.setStyleSheet("color:rgb(255,255,255);\n"
"font-size: 70px;\n"
"font-family: Rockwell;\n"
"font-weight: bold;\n"
"text-align: center;")
        self.result_text.setWordWrap(True)
        self.result_text.setAlignment(QtCore.Qt.AlignCenter)
        self.result_text.setObjectName("result_text")

        self.total_text = QtWidgets.QLabel(Form)
        self.total_text.setGeometry(QtCore.QRect(450, 520, 1100, 700))
        self.total_text.setStyleSheet("color:rgb(255,255,255);\n"
"font-size: 60px;\n"
"font-family: Rockwell;\n"
"font-weight: bold;\n"
"text-align: center;")
        self.total_text.setWordWrap(True)
        self.total_text.setAlignment(QtCore.Qt.AlignCenter)
        self.total_text.setObjectName("total")

        self.gif_reactive = QtWidgets.QLabel(Form)
        self.gif_reactive.setGeometry(QtCore.QRect(1300, 420, 500, 500))
        self.movie = QtGui.QMovie('stand_by.gif')
        self.gif_reactive.setMovie(self.movie)
        self.movie.start()
        self.gif_reactive.setObjectName("gif_reactive")

        self.update_gif.connect(self.update_gif_label)


    def update_gif_label(self, gif_path):
        if gif_path:
            self.gif_reactive.setMovie(QtGui.QMovie(gif_path))
            self.gif_reactive.movie().start()
        else:
            self.gif_reactive.clear()

    def update_results(self, good_ans_count, partial_ans_count, bad_ans_count, not_ans_count):
        self.result_text.setText(f" {good_ans_count}\n {bad_ans_count}\n {partial_ans_count}\n {not_ans_count}")
        self.total_text.setText(f"{good_ans_count}")
        if good_ans_count == 5:
            self.update_gif.emit('1.gif')
        elif good_ans_count == 4:
            self.update_gif.emit('2.gif')
        elif good_ans_count == 3:
            self.update_gif.emit('3.gif')
        elif good_ans_count == 2:
            self.update_gif.emit('4.gif')
        elif good_ans_count == 1:
            self.update_gif.emit('5.gif')
        else:
            self.update_gif.emit('6.gif')


    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("ResultWindow", "Results"))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_ResultWindow()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
