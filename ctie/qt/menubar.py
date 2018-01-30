from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from .QChrootFileDirDialog import *

class Menubar():
    def __init__(self, ui, menubar):
        self.ui = ui
        self.menubar = menubar

        menuBatch = menubar.addMenu('&Batch')

        trim_left_top = QAction('Trim Left-Top', self.menubar)
        trim_left_top.triggered.connect(self.onTrimLeftTop)
        menuBatch.addAction(trim_left_top)

        trim_right_bottom = QAction('Trim Right-Bottom', self.menubar)
        trim_right_bottom.triggered.connect(self.onTrimRightBottom)
        menuBatch.addAction(trim_right_bottom)

    def onTrimLeftTop(self):
        self.ui.core.batchTrimLeftTop()

    def onTrimRightBottom(self):
        self.ui.core.batchTrimRightBottom()
