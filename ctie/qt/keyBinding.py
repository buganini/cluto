from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *

class KeyBinding():
    def __init__(self, ui):
        self.ui = ui

        self.page_up = QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_PageUp), self.ui.ui)
        self.page_up.activated.connect(self.onPageUp)

        self.page_down = QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_PageDown), self.ui.ui)
        self.page_down.activated.connect(self.onPageDown)

    def onPageUp(self):
        self.ui.core.selectPrevItem()


    def onPageDown(self):
        self.ui.core.selectNextItem()