from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer

class QAutoEdit(QPlainTextEdit):
    focusIn = pyqtSignal()
    focusOut = pyqtSignal()

    def __init__(self, fontSize=None):
        QPlainTextEdit.__init__(self)
        font = QtGui.QFont("Consolas")
        font.setStyleHint(QtGui.QFont.TypeWriter)
        if not fontSize is None:
            font.setPointSize(fontSize)
        self.timer = None
        self.prevContent = None
        self.blocked = False
        self.setFont(font)

        self.updateHeight()
        self.textChanged.connect(self.onTextChanged)

    def autoFit(self, immediate):
        if self.timer:
            self.timer.stop()
        if immediate:
            self._autoFit()
        else:
            self.timer = QTimer(self)
            self.timer.singleShot(250, self._autoFit)

    def _autoFit(self):
        if self.blocked:
            return
        content = self.toPlainText()
        if self.prevContent != content:
            self.prevContent = content
            self.updateHeight()

    def focusInEvent(self, event):
        QPlainTextEdit.focusInEvent(self, event)
        self.focusIn.emit()

    def focusOutEvent(self, event):
        QPlainTextEdit.focusOutEvent(self, event)
        self.focusOut.emit()

    def setPlainText(self, text):
        QPlainTextEdit.setPlainText(self, text)
        self.autoFit(True)

    def setPlaceholderText(self, text):
        QPlainTextEdit.setPlaceholderText(self, text)
        self.updateHeight()

    def onTextChanged(self):
        self.autoFit(True)

    def resizeEvent(self, newSize):
        self.prevContent = None
        QPlainTextEdit.resizeEvent(self, newSize)
        self.autoFit(False)

    def updateHeight(self):
        currText = self.toPlainText()
        if currText:
            self.setFixedHeight(self.getContentHeight())
        else:
            self.blocked = True
            QPlainTextEdit.setPlainText(self, self.placeholderText())
            self.setFixedHeight(self.getContentHeight())
            QPlainTextEdit.setPlainText(self, "")
            self.blocked = False

    # https://stackoverflow.com/questions/45028105/get-the-exact-height-of-qtextdocument-in-pixels
    def getContentHeight(self):
        doc = self.document()
        layout = doc.documentLayout()
        h = 0
        b = doc.begin()
        while b != doc.end():
            h += layout.blockBoundingRect(b).height()
            b = b.next()

        # magic formula: I do not know why the document margin is already
        # once included in the height of the last block, and I do not know
        # why there must be the number 1 at the end... but it works
        return h + doc.documentMargin() + 2 * self.frameWidth() + 1
