from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from .QTagEdit import *

class CollationView():
    class QViewArea(QWidget):
        def __init__(self, scrollArea):
            QWidget.__init__(self)
            self.scrollArea = scrollArea
            self.scale = 1
            self.item = None

        def mouseReleaseEvent(self, event):
            self.zoomFit()

        def wheelEvent(self, event):
            self.scale += event.angleDelta().y()/4096
            self.scale = min(self.scale, 10)
            self.scale = max(self.scale, 0.03)
            self.updateGeometry()

        def updateGeometry(self):
            self.resize(self.w*self.scale, self.h*self.scale)
            self.update()

        def paintEvent(self, event):
            if not self.item:
                return
            item = self.item
            painter = QtGui.QPainter(self)
            painter.scale(self.scale, self.scale)
            item.drawQT(painter)

        def zoomFit(self):
            xscale = self.scrollArea.viewport().width() / self.w
            yscale = self.scrollArea.viewport().height() / self.h
            self.scale = min(xscale, yscale)
            self.updateGeometry()

        def update_item(self):
            self.item = self.ui.core.getCurrentItem()
            if not self.item:
                return
            if len(self.ui.core.selections) == 1:
                self.item = self.item.children[self.ui.core.selections[0]]
            self.w, self.h = self.item.getSize()
            self.zoomFit()
            return self.item

    def __init__(self, ui, splitter, collationView, collationViewAreaScroller):
        self.ui = ui
        self.splitter = splitter
        self.collationView = collationView
        self.collationViewAreaScroller = collationViewAreaScroller
        self.collationViewArea = self.QViewArea(self.collationViewAreaScroller)
        self.collationViewArea.ui = ui
        self.collationViewAreaScroller.setWidget(self.collationViewArea)
        self.edit = QTagEdit()
        self.edit.textChanged.connect(self.editTextChanged)
        self.collationView.addWidget(self.edit)
        self.item = None
        self.blockTextChanged = False
        self.blockItemUpdated = False

    def onItemChanged(self):
        self.update_item()

    def onSelectionChanged(self):
        self.update_item()

    def onContentChanged(self):
        self.update_item()

    def onSetCollationMode(self):
        enabled = self.ui.core.collationMode
        self.splitter.setSizes([1, (0, 1)[enabled]])
        self.splitter.handle(1).setEnabled(enabled)
        self.collationViewArea.update_item()

    def onSetFocusTag(self):
        tag = self.ui.core.focusTag
        self.blockItemUpdated = True
        self.edit.setPlainText(self.item.getTag(tag))
        self.blockItemUpdated = False

    def editTextChanged(self):
        if self.blockItemUpdated:
            return
        tag = self.ui.core.focusTag
        self.blockItemUpdated = True
        self.item.setTag(tag, self.edit.toPlainText())
        self.blockItemUpdated = False

    def update_item(self):
        if self.item:
            self.item.removeListener(self.onItemUpdated)
        self.item = self.collationViewArea.update_item()
        self.item.addListener(self.onItemUpdated)
        self.onSetFocusTag()

    def onItemUpdated(self):
        if self.blockItemUpdated:
            return
        self.onSetFocusTag()