from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from .QChrootFileDirDialog import *
from .regexManager import *
from .edgeDialog import *

class Menubar():
    def __init__(self, ui, menubar):
        self.ui = ui
        self.menubar = menubar

        menuBatch = menubar.addMenu('&Batch')

        trim = QAction('Trim', self.menubar)
        trim.triggered.connect(self.onTrim)
        menuBatch.addAction(trim)

        autopaste = QAction('Auto Paste', self.menubar)
        autopaste.triggered.connect(self.onAutoPaste)
        menuBatch.addAction(autopaste)

        menuOCR = menubar.addMenu('&OCR')
        regex = QAction('Regular Expression', self.menubar)
        regex.triggered.connect(self.onRegex)
        menuOCR.addAction(regex)

    def onTrim(self):
        EdgeDialog(self.ui, "Batch Trim", "Margin", 5, self.doTrim)

    def doTrim(self, left, top, right, bottom, margin):
        self.ui.core.batchTrim(left, top, right, bottom, margin)

    def onAutoPaste(self):
        self.ui.core.autoPaste()

    def onRegex(self):
        RegexManager(self.ui)
