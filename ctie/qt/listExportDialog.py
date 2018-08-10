from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import uic
from .QAutoEdit import *
from worker import JobHandler
import os
import json
import re

class ListExportDialog(QtCore.QObject):
    progress_signal = pyqtSignal(int, int, bool)

    def __init__(self, ui):
        QtCore.QObject.__init__(self)
        self.ui = ui
        self.ui.uiref["list_export_dialog"] = self

        self.exports = list(self.ui.core.exports)

        self.exportui = uic.loadUi(os.path.join(ui.app_path, "listExportDialog.ui"))

        self.edit_outputdir = self.exportui.findChild(QLineEdit, "edit_outputdir")
        self.btn_browse = self.exportui.findChild(QToolButton, "btn_browse")
        self.btn_browse.clicked.connect(self.onBrowse)

        self.edit_content = QAutoEdit()
        self.edit_content.setPlainText("")
        edit_content_frame = self.exportui.findChild(QGridLayout, "edit_content_frame")
        edit_content_frame.addWidget(self.edit_content)

        # Message
        self.message = self.exportui.findChild(QLabel, "message")

        # Buttons
        self.buttons = self.exportui.findChild(QDialogButtonBox, "buttons")
        self.btn_export = self.buttons.button(QDialogButtonBox.Apply)
        self.btn_export.setText("Export")
        self.btn_export.clicked.connect(self.onApply)
        self.buttons.button(QDialogButtonBox.Close).clicked.connect(self.onClose)

        self.progress_dialog = None
        self.progress_signal.connect(self._onProgress)

        self.exportui.show()

    def onBrowse(self):
        outputdir = QFileDialog.getExistingDirectory(self.exportui, u"Select Output Directory")
        if outputdir:
            self.edit_outputdir.setText(outputdir)

    def onApply(self):
        self.ui.core.worker.addFgJob(self)

    def __call__(self):
        self.handler = JobHandler()
        outputdir = self.edit_outputdir.text()
        content = self.edit_content.toPlainText()
        self.ui.core.list_export(outputdir, content, self.handler, self.onProgress)

    def onProgress(self, done, total, finished):
        self.progress_signal.emit(done, total, finished)

    def _onProgress(self, done, total, finished):
        if finished:
            if self.progress_dialog and not self.progress_dialog.wasCanceled():
                self.progress_dialog.hide()
            self.progress_dialog = None
        else:
            if self.progress_dialog is None:
                self.progress_dialog = QProgressDialog("Exporting...", "Abort", done, total, self.exportui)
                self.progress_dialog.canceled.connect(self.abort)
                self.progress_dialog.setAutoReset(False)
                self.progress_dialog.setAutoClose(False)
                self.progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
                self.progress_dialog.show()
            self.progress_dialog.setValue(done)

    def abort(self):
        self.handler.cancel()

    def onClose(self):
        self.exportui.close()
        self.ui.uiref.pop("list_export_dialog", None)