import os
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import uic
from datetime import datetime

class LoadDialog(QtCore.QObject):
    class TableModel(QtCore.QAbstractTableModel):
        def __init__(self, savedir):
            QtCore.QAbstractTableModel.__init__(self)
            if os.path.exists(savedir):
                files = os.listdir(savedir)
                times = [os.path.getmtime(os.path.join(savedir, x)) for x in files]
                l = list(zip(files, times))
                l.sort(key=lambda x:(-x[1], x[0]))
                self.data = [x[0] for x in l]
                self.time = [datetime.fromtimestamp(x[1]).strftime("%c") for x in l]
            else:
                self.data = []
                self.time = []

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
        self.ui.uiref["load_dialog"] = self
        self.loadui = uic.loadUi(os.path.join(ui.app_path, "loadDialog.ui"))

        self.workspace_path = self.loadui.findChild(QLineEdit, "workspace_path")
        self.btn_workspace = self.loadui.findChild(QToolButton, "btn_workspace")
        self.btn_workspace.clicked.connect(self.onBrowse)

        self.label_not_configured = self.loadui.findChild(QLabel, "label_not_configured")

        self.status = self.loadui.findChild(QLabel, "status")
        self.status.setStyleSheet("QLabel {color:red;}")

        self.table = self.loadui.findChild(QTableView, "table_data")
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)

        self.buttons = self.loadui.findChild(QDialogButtonBox, "buttons")
        self.buttons.accepted.connect(self.accepted)
        self.buttons.rejected.connect(self.rejected)

        self.label_not_configured.hide()
        self.table.hide()

        self.loadui.show()

        if self.ui.core.workspace:
            self.loadWorkspace(self.ui.core.workspace)
        else:
            self.onBrowse()

    def onBrowse(self):
        workspace = QFileDialog.getExistingDirectory(self.loadui, "Select Workspace Directory")
        if workspace:
            self.loadWorkspace(workspace)

    def loadWorkspace(self, workspace):
        self.workspace_path.setText(workspace)
        storagedir = self.ui.core.getStorageDir(workspace)
        if os.path.exists(storagedir):
            self.table.show()
            self.label_not_configured.hide()
            self.model = self.TableModel(os.path.join(storagedir, "save"))
            self.table.setModel(self.model)

            header = self.table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

            if len(self.model.data)==0:
                self.status.setText("No saved data.")
        else:
            self.model = None
            self.label_not_configured.show()
            self.table.hide()

    @QtCore.pyqtSlot()
    def accepted(self):
        if self.model:
            selected = self.table.selectionModel().selectedRows()
            if selected:
                fn = self.model.data[selected[0].row()]
                self.ui.core.load(self.workspace_path.text(), fn)
            else:
                self.ui.core.load(self.workspace_path.text(), None)
        else:
            self.ui.core.load(self.workspace_path.text(), None)
        self.close()

    @QtCore.pyqtSlot()
    def rejected(self):
        self.close()

    def close(self):
        self.loadui.close()
        self.ui.uiref.pop("load_dialog", None)