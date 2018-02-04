import os
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import uic
from datetime import datetime

class SetTagDialog(QtCore.QObject):
    def __init__(self, ui):
        QtCore.QObject.__init__(self)
        self.ui = ui
        self.ui.uiref["set_tag_dialog"] = self
        self.settagui = uic.loadUi(os.path.join(ui.app_path, "setTagDialog.ui"))

        self.edit_key = self.settagui.findChild(QLineEdit, "edit_key")
        self.edit_value = self.settagui.findChild(QLineEdit, "edit_value")
        self.chk_isformula = self.settagui.findChild(QCheckBox, "chk_isformula")

        self.buttons = self.settagui.findChild(QDialogButtonBox, "buttons")
        self.buttons.accepted.connect(self.accepted)
        self.buttons.rejected.connect(self.rejected)

        self.settagui.show()

    @QtCore.pyqtSlot()
    def accepted(self):
        key = self.edit_key.text()
        value = self.edit_value.text()
        isFormula = self.chk_isformula.isChecked()
        self.ui.core.batchSetTag(key, value, isFormula)
        self.close()

    @QtCore.pyqtSlot()
    def rejected(self):
        self.close()

    def close(self):
        self.settagui.close()
        self.ui.uiref.pop("set_tag_dialog", None)