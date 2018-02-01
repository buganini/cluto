import os
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import *

class ItemList(QObject):
    class QClickableWidget(QWidget):
        clicked = pyqtSignal(QWidget)

        def mouseReleaseEvent(self, *args):
            self.clicked.emit(self)

    def __init__(self, ui, listView, scroller):
        QObject.__init__(self)
        self.ui = ui
        self.listView = listView
        self.scroller = scroller
        self.uiMap = {}

    def onLevelChanged(self):
        self.reset()

    def onItemListChanged(self):
        self.reset()

    def onItemFocused(self, item):
        widget = self.uiMap[item]
        self.scroller.ensureWidgetVisible(widget, 0, 50)
        widget.setStyleSheet("background-color:rgba(50,50,255,30);")

    def onItemBlurred(self, item):
        widget = self.uiMap[item]
        if widget: # could be None when level changed
            widget.setStyleSheet("background-color:auto;")

    def reset(self):
        for i in reversed(range(self.listView.count())):
            self.listView.itemAt(i).widget().deleteLater()
        self.uiMap = {}

        currentItem = self.ui.core.getCurrentItem()
        for item in self.ui.core.items:
            layout = QVBoxLayout()
            layout.setSpacing(0)

            img = QLabel()
            img.setStyleSheet("padding: 10px;")
            img.setAlignment(QtCore.Qt.AlignCenter)
            item.drawThumbnailQT(img, 300, 200)
            layout.addWidget(img)

            label = QLabel()
            label.setStyleSheet("padding: 10px;")
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setText(os.path.basename(item.path))
            layout.addWidget(label)

            widget = self.QClickableWidget()
            widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
            widget.setLayout(layout)
            widget.item = item
            widget.clicked.connect(self.onItemSelected)

            self.uiMap[item] = widget

            self.listView.addWidget(widget)

            if item == currentItem:
                self.onItemFocused(item)


    @pyqtSlot(QWidget)
    def onItemSelected(self, widget):
        self.ui.core.selectItemByIndex(widget.item.getIndex())
