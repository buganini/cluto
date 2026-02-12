from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *

class KeyBinding():
    def __init__(self, ui):
        self.ui = ui

        self.ctrl_a = QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL | QtCore.Qt.Key_A), self.ui.ui)
        self.ctrl_a.activated.connect(self.onCtrlA)

        self.ctrl_c = QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL | QtCore.Qt.Key_C), self.ui.ui)
        self.ctrl_c.activated.connect(self.onCtrlC)

        self.ctrl_v = QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL | QtCore.Qt.Key_V), self.ui.ui)
        self.ctrl_v.activated.connect(self.onCtrlV)

        self.delete = QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Delete), self.ui.ui)
        self.delete.activated.connect(self.onDelete)

        self.page_up = QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_PageUp), self.ui.ui)
        self.page_up.activated.connect(self.onPageUp)

        self.page_down = QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_PageDown), self.ui.ui)
        self.page_down.activated.connect(self.onPageDown)

        self.ctrl_page_up = QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL | QtCore.Qt.Key_PageUp), self.ui.ui)
        self.ctrl_page_up.activated.connect(self.onCtrlPageUp)

        self.ctrl_page_down = QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL | QtCore.Qt.Key_PageDown), self.ui.ui)
        self.ctrl_page_down.activated.connect(self.onCtrlPageDown)


    def onCtrlA(self):
        self.ui.core.selectAllChildren()

    def onCtrlC(self):
        self.ui.core.copy()

    def onCtrlV(self):
        self.ui.core.paste()

    def onDelete(self):
        self.ui.core.deleteSelectedChildren()

    def onPageUp(self):
        if self.ui.core.collationMode:
            self.ui.core.selectPrevChild()
        else:
            self.ui.core.selectPrevItem()

    def onPageDown(self):
        if self.ui.core.collationMode:
            self.ui.core.selectNextChild()
        else:
            self.ui.core.selectNextItem()

    def onCtrlPageUp(self):
        if self.ui.core.collationMode:
            self.ui.core.selectPrevItem()
        else:
            self.ui.core.selectPrevChild()

    def onCtrlPageDown(self):
        if self.ui.core.collationMode:
            self.ui.core.selectNextItem()
        else:
            self.ui.core.selectNextChild()