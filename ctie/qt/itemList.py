import os
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import *
from .QThumbnail import QThumbnail
from .QAutoEdit import *

class ItemList(QObject):
    class QClickableWidget(QWidget):
        clicked = pyqtSignal(QWidget)

        def mouseReleaseEvent(self, *args):
            self.clicked.emit(self)

    def __init__(self, ui, listView, scroller, containerListSettings, btnApply):
        QObject.__init__(self)
        self.ui = ui
        self.listView = listView
        self.scroller = scroller
        self.edit_filter = QAutoEdit()
        self.edit_filter.setPlaceholderText("Filter")
        self.edit_sort_key = QAutoEdit()
        self.edit_sort_key.setPlaceholderText("Sort By")
        containerListSettings.addWidget(self.edit_filter)
        containerListSettings.addWidget(self.edit_sort_key)
        btnApply.clicked.connect(self.onApply)
        self.uiMap = {}

    def onProjectChanged(self):
        self.reset()

    def onLevelChanged(self):
        self.reset()

    def onItemListChanged(self):
        self.reset()

    def onItemFocused(self, item):
        widget = self.uiMap[item]
        self.scroller.ensureWidgetVisible(widget, 0, 50)
        widget.setStyleSheet("background-color:rgba(50,50,255,30);")

    def onItemBlurred(self, item):
        widget = self.uiMap.get(item)
        if widget: # could be None when level changed
            widget.setStyleSheet("background-color:auto;")

    def reset(self):
        for i in reversed(range(self.listView.count())):
            self.listView.itemAt(i).widget().deleteLater()
        self.uiMap = {}

        currentItem = self.ui.core.getCurrentItem()
        for index, item in enumerate(self.ui.core.items):
            layout = QVBoxLayout()
            layout.setSpacing(0)

            img = QThumbnail(item)
            img.setStyleSheet("padding: 10px;")
            layout.addWidget(img)

            label = QLabel()
            label.setStyleSheet("padding: 10px;")
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setText(item.getTitle())
            layout.addWidget(label)

            widget = self.QClickableWidget()
            widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
            widget.setLayout(layout)
            widget.item = item
            widget.index = index
            widget.clicked.connect(self.onItemSelected)

            self.uiMap[item] = widget

            self.listView.addWidget(widget)

            if item == currentItem:
                self.onItemFocused(item)

    def onItemTreeChanged(self):
        self.edit_filter.setPlainText(self.ui.core.filter_text)
        self.edit_sort_key.setPlainText(self.ui.core.sort_key_text)

    @pyqtSlot(QWidget)
    def onItemSelected(self, widget):
        self.ui.core.selectItemByIndex(widget.index)

    @pyqtSlot(bool)
    def onApply(self, checked):
        self.ui.core.setItemsSettings(self.edit_filter.toPlainText(), self.edit_sort_key.toPlainText())