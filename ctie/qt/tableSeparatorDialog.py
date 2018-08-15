import os
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import uic

class TableSeparatorDialog(QtCore.QObject):
    def __init__(self, ui, title, callback):
        QtCore.QObject.__init__(self)
        self.ui = ui
        self.callback = callback
        self.ui.uiref["table_separatpr_dialog"] = self
        self.edgeui = uic.loadUi(os.path.join(ui.app_path, "tableSeparatorDialog.ui"))

        self.edgeui.setWindowTitle(title)

        self.edit_min_row_separator_percentage = self.edgeui.findChild(QSpinBox, "edit_min_row_separator_percentage")
        self.edit_min_col_separator_percentage = self.edgeui.findChild(QSpinBox, "edit_min_col_separator_percentage")

        self.chk_row_separator = self.edgeui.findChild(QCheckBox, "chk_row_separator")
        self.chk_col_separator = self.edgeui.findChild(QCheckBox, "chk_col_separator")

        self.buttons = self.edgeui.findChild(QDialogButtonBox, "buttons")
        self.buttons.accepted.connect(self.accepted)
        self.buttons.rejected.connect(self.rejected)

        self.edgeui.show()

    @QtCore.pyqtSlot()
    def accepted(self):
        self.callback(
            self.chk_row_separator.isChecked(),
            self.edit_min_row_separator_percentage.value(),
            self.chk_col_separator.isChecked(),
            self.edit_min_col_separator_percentage.value()
        )
        self.close()

    @QtCore.pyqtSlot()
    def rejected(self):
        self.close()

    def close(self):
        self.edgeui.close()
        self.ui.uiref.pop("table_separatpr_dialog", None)