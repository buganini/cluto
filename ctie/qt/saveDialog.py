import os
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import uic
from datetime import datetime

class SaveDialog(QtCore.QObject):
    class TableModel(QtCore.QAbstractTableModel):
        def __init__(self, savedir):
            QtCore.QAbstractTableModel.__init__(self)
            self.data = os.listdir(savedir)
            self.time = [datetime.fromtimestamp(os.path.getmtime(os.path.join(savedir, x))).strftime("%c") for x in self.data]

        def rowCount(self, parent):
            return len(self.data)

        def columnCount(self, parent):
            return 2

        def headerData(self, section, orientation, role):
            if role == QtCore.Qt.DisplayRole:
                if orientation == QtCore.Qt.Horizontal:
                    return ["Name", "Last Modified"][section]

        def data(self, index, role):
            if not index.isValid():
                return None
            if role == QtCore.Qt.DisplayRole:
                r = index.row()
                c = index.column()
                if c==0:
                    return self.data[r]
                elif c==1:
                    return self.time[r]

    def __init__(self, ui):
        QtCore.QObject.__init__(self)
        self.ui = ui
        self.ui.uiref["save_dialog"] = self
        self.loadui = uic.loadUi(os.path.join(ui.app_path, "saveDialog.ui"))

        self.edit_save = self.loadui.findChild(QLineEdit, "edit_save")

        self.table = self.loadui.findChild(QTableView, "table_data")
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)

        self.model = self.TableModel(self.ui.core.savedir)
        self.table.setModel(self.model)

        self.table.selectionModel().clearSelection()
        self.table.selectionModel().selectionChanged.connect(self.onSelectionChanged)


        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        self.buttons = self.loadui.findChild(QDialogButtonBox, "buttons")
        self.buttons.accepted.connect(self.onAccepted)
        self.buttons.rejected.connect(self.onRejected)
        self.btn_accept = self.buttons.button(QDialogButtonBox.Ok)

        self.edit_save.textChanged.connect(self.onEditSaveChanged)
        self.onEditSaveChanged()

        self.loadui.show()

    @QtCore.pyqtSlot(QtCore.QItemSelection, QtCore.QItemSelection)
    def onSelectionChanged(self, selected, deselected):
        fn = self.model.data[self.table.selectionModel().selectedRows()[0].row()]
        self.edit_save.setText(fn)

    def onEditSaveChanged(self, value=None):
        if self.edit_save.text():
            self.btn_accept.setEnabled(True)
        else:
            self.btn_accept.setEnabled(False)

    @QtCore.pyqtSlot()
    def onAccepted(self):
        fn = self.edit_save.text()
        self.ui.core.save(os.path.join(self.ui.core.savedir, fn))
        self.close()

    @QtCore.pyqtSlot()
    def onRejected(self):
        self.close()

    def close(self):
        self.loadui.close()
        self.ui.uiref.pop("save_dialog", None)