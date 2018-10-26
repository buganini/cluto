import os
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import *
from .QThumbnail import QThumbnail
from .QAutoEdit import *

class ItemList(QObject):
    class ItemWidget(QFrame):
        clicked = pyqtSignal(QFrame)

        def __init__(self):
            QFrame.__init__(self)
            self.setObjectName(str(id(self)))

        def mouseReleaseEvent(self, *args):
            self.clicked.emit(self)

        def updateUI(self, focus):
            css = []
            css.append("QFrame#"+str(id(self))+" {")
            if "DUP" in self.item.flags:
                css.append("background: rgba(255,50,50,50);")
            css.append("border-style: outset;")
            css.append("border-width: 3px;")
            if self.item == focus:
                css.append("border-color: blue;")
            else:
                css.append("border-color: transparent;")
            css.append("}")
            self.setStyleSheet("".join(css))

    def __init__(self, ui, listView, scroller, containerListSettings, btnApply):
        QObject.__init__(self)
        self.ui = ui
        self.listView = listView
        self.scroller = scroller
        self.edit_filter = QAutoEdit()
        self.edit_filter.setPlaceholderText("Filter")
        self.edit_sort_key = QAutoEdit()
        self.edit_sort_key.setPlaceholderText("Sort By")
        self.chk_dups_only = QCheckBox()
        self.chk_dups_only.setText("Duplicateds only")
        containerListSettings.addWidget(self.edit_filter)
        containerListSettings.addWidget(self.edit_sort_key)
        containerListSettings.addWidget(self.chk_dups_only)
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
        widget.updateUI(item)

    def onItemBlurred(self, item):
        widget = self.uiMap.get(item)
        if widget: # could be None when level changed
            widget.updateUI(None)

    def reset(self):
        for i in reversed(range(self.listView.count())):
            self.listView.itemAt(i).widget().deleteLater()
        self.uiMap = {}

        currentItem = self.ui.core.getCurrentItem()
        for index, item in enumerate(self.ui.core.items):
            layout = QVBoxLayout()
            layout.setSpacing(0)
            layout.setAlignment(QtCore.Qt.AlignCenter)

            img = QThumbnail(item)
            layout.addWidget(img)

            label = QLabel()
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setText(item.getTitle())
            layout.addWidget(label)

            widget = self.ItemWidget()
            widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
            widget.setLayout(layout)
            widget.item = item
            widget.index = index
            widget.clicked.connect(self.onItemSelected)

            self.uiMap[item] = widget

            self.listView.addWidget(widget)

            widget.updateUI(currentItem)

    def onItemTreeChanged(self):
        self.edit_filter.setPlainText(self.ui.core.filter_text)
        self.edit_sort_key.setPlainText(self.ui.core.sort_key_text)
        self.chk_dups_only.setChecked(self.ui.core.dups_only)

    @pyqtSlot(QFrame)
    def onItemSelected(self, widget):
        self.ui.core.selectItemByIndex(widget.index)

    @pyqtSlot(bool)
    def onApply(self, checked):
        self.ui.core.setItemsSettings(self.edit_filter.toPlainText(), self.edit_sort_key.toPlainText(), self.chk_dups_only.isChecked())