from PyQt5.QtWidgets import *
from PyQt5 import QtGui

class QTagEdit(QPlainTextEdit):
    def __init__(self):
        QPlainTextEdit.__init__(self)
        font = QtGui.QFont("Consolas")
        font.setStyleHint(QtGui.QFont.TypeWriter)
        self.setFont(font)