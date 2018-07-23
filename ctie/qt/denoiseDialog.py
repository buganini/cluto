import os
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import uic

class DenoiseDialog(QtCore.QObject):
    def __init__(self, ui, initial_min_width, initial_min_height, callback):
        QtCore.QObject.__init__(self)
        self.ui = ui
        self.callback = callback
        self.ui.uiref["denoise_dialog"] = self
        self.denoiseui = uic.loadUi(os.path.join(ui.app_path, "denoiseDialog.ui"))

        self.edit_min_width = self.denoiseui.findChild(QSpinBox, "min_width")
        self.edit_min_width.setValue(initial_min_width)

        self.edit_min_height = self.denoiseui.findChild(QSpinBox, "min_height")
        self.edit_min_height.setValue(initial_min_height)

        self.buttons = self.denoiseui.findChild(QDialogButtonBox, "buttons")
        self.buttons.accepted.connect(self.accepted)
        self.buttons.rejected.connect(self.rejected)

        self.denoiseui.show()

    @QtCore.pyqtSlot()
    def accepted(self):
        self.callback(
            self.edit_min_width.value(),
            self.edit_min_height.value()
        )
        self.close()

    @QtCore.pyqtSlot()
    def rejected(self):
        self.close()

    def close(self):
        self.denoiseui.close()
        self.ui.uiref.pop("denoise_dialog", None)