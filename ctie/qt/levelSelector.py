from PyQt5.QtWidgets import *
from functools import partial
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class LevelSelector(QObject):
    def __init__(self, ui, selector):
        QObject.__init__(self)
        self.ui = ui
        self.selector = selector
        self.selector.currentIndexChanged.connect(self.onCurrentIndexChanged)

    def onItemTreeChanged(self):
        current = self.selector.currentIndex()
        self.selector.clear()
        level = self.ui.core.getLevel()
        for i in range(level):
            self.selector.addItem("{}".format(i))
        if current >= 0 and current < level:
            self.selector.setCurrentIndex(current)

    @pyqtSlot(int)
    def onCurrentIndexChanged(self, index):
        self.ui.core.setLevel(index)
