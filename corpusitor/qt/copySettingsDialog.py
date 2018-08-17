import os
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import uic

class CopySettingsDialog(QtCore.QObject):
    class TagsTableModel(QtCore.QAbstractTableModel):
        def __init__(self, ui):
            QtCore.QAbstractTableModel.__init__(self)
            self.data = list(ui.core.getTags())
            self.checked = []
            self.data.sort()
            for t in self.data:
                self.checked.append(t in ui.core.copy_tags)

        def rowCount(self, parent):
            return len(self.data)

        def columnCount(self, parent):
            return 1

        def headerData(self, section, orientation, role):
            if role == QtCore.Qt.DisplayRole:
                if orientation == QtCore.Qt.Horizontal:
                    return ["Tag"][section]
                if orientation == QtCore.Qt.Vertical:
                    return str(section+1)

        def data(self, index, role):
            if not index.isValid():
                return None
            r = index.row()
            if role == QtCore.Qt.CheckStateRole:
                return (QtCore.Qt.Unchecked, QtCore.Qt.Checked)[self.checked[r]]
            if role == QtCore.Qt.DisplayRole:
                return self.data[r]

        def flags(self, index):
            flags = QtCore.QAbstractTableModel.flags(self, index)
            flags = flags | QtCore.Qt.ItemIsUserCheckable
            return flags

        def setData(self, index, value, role=QtCore.Qt.EditRole):
            if role == QtCore.Qt.CheckStateRole:
                r = index.row()
                self.checked[r] = value == QtCore.Qt.Checked
            return True

    def __init__(self, ui):
        QtCore.QObject.__init__(self)
        self.ui = ui
        self.ui.uiref["copy_settings_dialog"] = self
        self.copysettingsui = uic.loadUi(os.path.join(ui.app_path, "copySettingsDialog.ui"))

        self.table_tags = self.copysettingsui.findChild(QTableView, "table_tags")

        self.model_tags = self.TagsTableModel(self.ui)
        self.table_tags.setModel(self.model_tags)

        header = self.table_tags.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        self.buttons = self.copysettingsui.findChild(QDialogButtonBox, "buttons")
        self.buttons.accepted.connect(self.onAccepted)
        self.buttons.rejected.connect(self.onRejected)

        self.copysettingsui.show()

    @QtCore.pyqtSlot()
    def onAccepted(self):
        tags = []
        for i in range(len(self.model_tags.data)):
            if self.model_tags.checked[i]:
                tags.append(self.model_tags.data[i])
        self.ui.core.updateCopyTags(tags)
        self.close()

    @QtCore.pyqtSlot()
    def onRejected(self):
        self.close()

    def close(self):
        self.copysettingsui.close()
        self.ui.uiref.pop("copy_settings_dialog", None)