from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from .QChrootFileDirDialog import *
from .regexManager import *
from .edgeDialog import *
from .pasteDialog import *
from .setTagDialog import *

class Menubar():
    def __init__(self, ui, menubar):
        self.ui = ui
        self.menubar = menubar

        menuBatch = menubar.addMenu('&Batch')

        trim = QAction('Trim', self.menubar)
        trim.triggered.connect(self.onTrim)
        menuBatch.addAction(trim)

        shrink = QAction('Shrink', self.menubar)
        shrink.triggered.connect(self.onShrink)
        menuBatch.addAction(shrink)

        autopaste = QAction('Auto Paste', self.menubar)
        autopaste.triggered.connect(self.onAutoPaste)
        menuBatch.addAction(autopaste)

        settag = QAction('Set Tag', self.menubar)
        settag.triggered.connect(self.onSetTag)
        menuBatch.addAction(settag)

        menuOCR = menubar.addMenu('&OCR')
        regex = QAction('Regular Expression', self.menubar)
        regex.triggered.connect(self.onRegex)
        menuOCR.addAction(regex)

    def onTrim(self):
        EdgeDialog(self.ui, "Batch Trim", "Margin", 5, self.doTrim)

    def doTrim(self, left, top, right, bottom, margin):
        self.ui.core.batchTrim(left, top, right, bottom, margin)

    def onShrink(self):
        EdgeDialog(self.ui, "Batch Shrink", "Amount", 1, self.doShrink)

    def doShrink(self, left, top, right, bottom, amount):
        self.ui.core.batchShrink(left, top, right, bottom, amount)

    def onAutoPaste(self):
        PasteDialog(self.ui)

    def onSetTag(self):
        SetTagDialog(self.ui)

    def onRegex(self):
        RegexManager(self.ui)
