from PyQt5.QtWidgets import *
from functools import partial
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class ItemFilter(QObject):
    def __init__(self, ui, edit_filter, btn_filter):
        QObject.__init__(self)
        self.ui = ui
        self.edit_filter = edit_filter
        self.btn_filter = btn_filter
        self.btn_filter.clicked.connect(self.onApply)

    def onItemTreeChanged(self):
        current = self.selector.currentIndex()
        self.selector.clear()
        level = self.ui.core.getLevel()
        for i in range(level):
            self.selector.addItem("{}".format(i))
        if current >= 0 and current < level:
            self.selector.setCurrentIndex(current)

    @pyqtSlot(bool)
    def onApply(self, checked):
        self.ui.core.setFilter(self.edit_filter.text())
