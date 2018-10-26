import os
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import uic

class PasteDialog(QtCore.QObject):
    def __init__(self, ui):
        QtCore.QObject.__init__(self)
        self.ui = ui
        self.ui.uiref["paste_dialog"] = self
        self.pasteui = uic.loadUi(os.path.join(ui.app_path, "pasteDialog.ui"))

        self.chk_empty = self.pasteui.findChild(QCheckBox, "chk_empty")
        self.chk_overlap = self.pasteui.findChild(QCheckBox, "chk_overlap")
        self.chk_overlap_aon = self.pasteui.findChild(QCheckBox, "chk_overlap_aon")
        self.chk_boundary = self.pasteui.findChild(QCheckBox, "chk_boundary")
        self.chk_boundary_aon = self.pasteui.findChild(QCheckBox, "chk_boundary_aon")

        self.chk_overlap.stateChanged.connect(self.chk_overlap_changed)
        self.chk_boundary.stateChanged.connect(self.chk_boundary_changed)

        self.chk_empty.setChecked(False)
        self.chk_overlap.setChecked(True)
        self.chk_overlap_aon.setChecked(True)
        self.chk_boundary.setChecked(True)
        self.chk_boundary_aon.setChecked(True)

        self.buttons = self.pasteui.findChild(QDialogButtonBox, "buttons")
        self.buttons.accepted.connect(self.accepted)
        self.buttons.rejected.connect(self.rejected)

        self.pasteui.show()

    @QtCore.pyqtSlot(int)
    def chk_overlap_changed(self, state):
        self.chk_overlap_aon.setEnabled(self.chk_overlap.isChecked())

    @QtCore.pyqtSlot(int)
    def chk_boundary_changed(self, state):
        self.chk_boundary_aon.setEnabled(self.chk_boundary.isChecked())

    @QtCore.pyqtSlot()
    def accepted(self):
        self.ui.core.batchPaste(self.chk_empty.isChecked(), self.chk_overlap.isChecked(), self.chk_overlap_aon.isChecked(), self.chk_boundary.isChecked(), self.chk_boundary_aon.isChecked())
        self.close()

    @QtCore.pyqtSlot()
    def rejected(self):
        self.close()

    def close(self):
        self.pasteui.close()
        self.ui.uiref.pop("paste_dialog", None)