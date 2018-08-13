from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import QtGui
from .QChrootFileDirDialog import *
from .regexManager import *
from .edgeDialog import *
from .denoiseDialog import *
from .pasteDialog import *
from .setTagDialog import *
from .listExportDialog import *
from .helper import *
import time

class Menubar(QtCore.QObject):
    def __init__(self, ui, menubar):
        QtCore.QObject.__init__(self)
        self.ui = ui
        self.menubar = menubar

        menuList = menubar.addMenu('&List')

        batchTrim = QAction('Trim', self.menubar)
        batchTrim.triggered.connect(self.onBatchTrim)
        menuList.addAction(batchTrim)

        batchShrink = QAction('Shrink', self.menubar)
        batchShrink.triggered.connect(self.onBatchShrink)
        menuList.addAction(batchShrink)

        batchDetectColSeparator = QAction('Detect column separator', self.menubar)
        batchDetectColSeparator.triggered.connect(self.onBatchDetectColSeparator)
        menuList.addAction(batchDetectColSeparator)

        batchDetectRowSeparator = QAction('Detect row separator', self.menubar)
        batchDetectRowSeparator.triggered.connect(self.onBatchDetectRowSeparator)
        menuList.addAction(batchDetectRowSeparator)

        batchColsToChildren = QAction('Columns to children', self.menubar)
        batchColsToChildren.triggered.connect(self.onBatchColsToChildren)
        menuList.addAction(batchColsToChildren)

        batchRowsToChildren = QAction('Rows to children', self.menubar)
        batchRowsToChildren.triggered.connect(self.onBatchRowsToChildren)
        menuList.addAction(batchRowsToChildren)

        batchDenoise = QAction('Denoise', self.menubar)
        batchDenoise.triggered.connect(self.onBatchDenoise)
        menuList.addAction(batchDenoise)

        batchAutoPaste = QAction('Auto Paste', self.menubar)
        batchAutoPaste.triggered.connect(self.onBatchAutoPaste)
        menuList.addAction(batchAutoPaste)

        batchSettag = QAction('Set Tag', self.menubar)
        batchSettag.triggered.connect(self.onBatchSetTag)
        menuList.addAction(batchSettag)

        listExport = QAction('Export', self.menubar)
        listExport.triggered.connect(self.onListExport)
        menuList.addAction(listExport)

        menuThis = menubar.addMenu('&This')

        thisTrim = QAction('Trim', self.menubar)
        thisTrim.triggered.connect(self.onThisTrim)
        menuThis.addAction(thisTrim)

        thisShrink = QAction('Shrink', self.menubar)
        thisShrink.triggered.connect(self.onThisShrink)
        menuThis.addAction(thisShrink)

        thisDetectColSeparator = QAction('Detect column separator', self.menubar)
        thisDetectColSeparator.triggered.connect(self.onThisDetectColSeparator)
        menuThis.addAction(thisDetectColSeparator)

        thisDetectRowSeparator = QAction('Detect row separator', self.menubar)
        thisDetectRowSeparator.triggered.connect(self.onThisDetectRowSeparator)
        menuThis.addAction(thisDetectRowSeparator)

        thisColsToChildren = QAction('Columns to children', self.menubar)
        thisColsToChildren.triggered.connect(self.onThisColsToChildren)
        menuThis.addAction(thisColsToChildren)

        thisRowsToChildren = QAction('Rows to children', self.menubar)
        thisRowsToChildren.triggered.connect(self.onThisRowsToChildren)
        menuThis.addAction(thisRowsToChildren)

        thisDenoise = QAction('Denoise', self.menubar)
        thisDenoise.triggered.connect(self.onThisDenoise)
        menuThis.addAction(thisDenoise)

        menuOCR = menubar.addMenu('&OCR')
        ocrRegex = QAction('Regular Expression', self.menubar)
        ocrRegex.triggered.connect(self.onOcrRegex)
        menuOCR.addAction(ocrRegex)

        self.progress_dialog = None

    def onBatchTrim(self):
        EdgeDialog(self.ui, "Batch Trim", "Margin", 5, self.doBatchTrim)

    def doBatchTrim(self, left, top, right, bottom, margin):
        self.ui.core.batchTrim(left, top, right, bottom, margin, self.onProgress)

    def onBatchDetectColSeparator(self):
        self.ui.core.batchDetectColSeparator(self.onProgress)

    def onBatchDetectRowSeparator(self):
        self.ui.core.batchDetectRowSeparator(self.onProgress)

    def onBatchColsToChildren(self):
        self.ui.core.batchColsToChildren(self.onProgress)

    def onBatchRowsToChildren(self):
        self.ui.core.batchRowsToChildren(self.onProgress)

    def onBatchShrink(self):
        EdgeDialog(self.ui, "Batch Shrink", "Amount", 1, self.doBatchShrink)

    def doBatchShrink(self, left, top, right, bottom, amount):
        self.ui.core.batchShrink(left, top, right, bottom, amount, self.onProgress)

    def onBatchDenoise(self):
        item = self.ui.core.getCurrentItem()
        if item:
            DenoiseDialog(self.ui, 5 * item.scaleFactor, 5 * item.scaleFactor, self.doBatchDenoise)

    def doBatchDenoise(self, min_width, min_height):
        self.ui.core.batchDenoise(min_width, min_height, self.onProgress)

    def onBatchAutoPaste(self):
        PasteDialog(self.ui)

    def onBatchSetTag(self):
        SetTagDialog(self.ui, self.doBatchSetTag)

    def doBatchSetTag(self, key, value, isFormula):
        self.ui.core.batchSetTag(key, value, isFormula, self.onProgress)

    def onListExport(self):
        ListExportDialog(self.ui)

    @UI
    def onProgress(self, done, total):
        if done==total:
            if self.progress_dialog and not self.progress_dialog.wasCanceled():
                self.progress_dialog.setValue(done)
                self.progress_dialog.hide()
            self.progress_dialog = None
        else:
            if self.progress_dialog is None:
                self.progress_dialog = QProgressDialog("Running batch task...", None, done, total, self.ui.ui)
                self.progress_dialog.setAutoReset(False)
                self.progress_dialog.setAutoClose(False)
                self.progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
                self.progress_dialog.show()
                time.sleep(0.05)
            self.progress_dialog.setValue(done)

    def onOcrRegex(self):
        RegexManager(self.ui)

    def onThisTrim(self):
        EdgeDialog(self.ui, "Trim", "Margin", 5, self.doThisTrim)

    def doThisTrim(self, left, top, right, bottom, margin):
        item = self.ui.core.getCurrentItem()
        if item:
            item.trim(left, top, right, bottom, margin)
            self.ui.onContentChanged()

    def onThisShrink(self):
        EdgeDialog(self.ui, "Shrink", "Amount", 1, self.doThisShrink)

    def doThisShrink(self, left, top, right, bottom, amount):
        item = self.ui.core.getCurrentItem()
        if item:
            item.shrink(left, top, right, bottom, amount)

    def onThisDetectColSeparator(self):
        item = self.ui.core.getCurrentItem()
        if item:
            item.detectColSeparator()
            self.ui.onContentChanged()

    def onThisDetectRowSeparator(self):
        item = self.ui.core.getCurrentItem()
        if item:
            item.detectRowSeparator()
            self.ui.onContentChanged()

    def onThisColsToChildren(self):
        item = self.ui.core.getCurrentItem()
        if item:
            item.colsToChildren()
            self.ui.onContentChanged()

    def onThisRowsToChildren(self):
        item = self.ui.core.getCurrentItem()
        if item:
            item.rowsToChildren()
            self.ui.onContentChanged()

    def onThisDenoise(self):
        item = self.ui.core.getCurrentItem()
        if item:
            DenoiseDialog(self.ui, 5 * item.scaleFactor, 5 * item.scaleFactor, self.doThisDenoise)

    def doThisDenoise(self, min_width, min_height):
        item = self.ui.core.getCurrentItem()
        if item:
            item.denoise(min_width, min_height)
            self.ui.onContentChanged()
