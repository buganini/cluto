import os
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import uic
from datetime import datetime

class EdgeDialog(QtCore.QObject):
    def __init__(self, ui, title, callback):
        QtCore.QObject.__init__(self)
        self.ui = ui
        self.callback = callback
        self.ui.uiref["edge_dialog"] = self
        self.trimui = uic.loadUi(os.path.join(ui.app_path, "edgeDialog.ui"))

        self.chk_left = self.trimui.findChild(QCheckBox, "chk_left")
        self.chk_top = self.trimui.findChild(QCheckBox, "chk_top")
        self.chk_right = self.trimui.findChild(QCheckBox, "chk_right")
        self.chk_bottom = self.trimui.findChild(QCheckBox, "chk_bottom")

        self.buttons = self.trimui.findChild(QDialogButtonBox, "buttons")
        self.buttons.accepted.connect(self.accepted)
        self.buttons.rejected.connect(self.rejected)

        self.trimui.show()

    @QtCore.pyqtSlot()
    def accepted(self):
        self.callback(
            self.chk_left.isChecked(),
            self.chk_top.isChecked(),
            self.chk_right.isChecked(),
            self.chk_bottom.isChecked()
        )
        self.close()

    @QtCore.pyqtSlot()
    def rejected(self):
        self.close()

    def close(self):
        self.trimui.close()
        self.ui.uiref.pop("edge_dialog", None)