import os
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import uic

class EdgeDialog(QtCore.QObject):
    def __init__(self, ui, title, value_name, initial_value, callback):
        QtCore.QObject.__init__(self)
        self.ui = ui
        self.callback = callback
        self.ui.uiref["edge_dialog"] = self
        self.edgeui = uic.loadUi(os.path.join(ui.app_path, "edgeDialog.ui"))

        self.edgeui.setWindowTitle(title)

        self.label_value_name = self.edgeui.findChild(QLabel, "label_value_name")
        self.label_value_name.setText(value_name)

        self.edit_value = self.edgeui.findChild(QSpinBox, "edit_value")
        self.edit_value.setValue(initial_value)

        self.chk_left = self.edgeui.findChild(QCheckBox, "chk_left")
        self.chk_top = self.edgeui.findChild(QCheckBox, "chk_top")
        self.chk_right = self.edgeui.findChild(QCheckBox, "chk_right")
        self.chk_bottom = self.edgeui.findChild(QCheckBox, "chk_bottom")

        self.buttons = self.edgeui.findChild(QDialogButtonBox, "buttons")
        self.buttons.accepted.connect(self.accepted)
        self.buttons.rejected.connect(self.rejected)

        self.edgeui.show()

    @QtCore.pyqtSlot()
    def accepted(self):
        self.callback(
            self.chk_left.isChecked(),
            self.chk_top.isChecked(),
            self.chk_right.isChecked(),
            self.chk_bottom.isChecked(),
            self.edit_value.value()
        )
        self.close()

    @QtCore.pyqtSlot()
    def rejected(self):
        self.close()

    def close(self):
        self.edgeui.close()
        self.ui.uiref.pop("edge_dialog", None)