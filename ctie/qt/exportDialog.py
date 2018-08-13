from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import uic
from .QAutoEdit import *
from worker import JobHandler
import os
import json
import re
import time
from datetime import datetime

class ExportDialog(QtCore.QObject):
    # http://apocalyptech.com/linux/qt/qtableview/
    class TableStyle(QProxyStyle):
        def drawPrimitive(self, element, option, painter, widget=None):
            """
            Draw a line across the entire row rather than just the column
            we're hovering over.  This may not always work depending on global
            style - for instance I think it won't work on OSX.
            """
            if element == self.PE_IndicatorItemViewItemDrop and not option.rect.isNull():
                option_new = QStyleOption(option)
                option_new.rect.setLeft(0)
                if widget:
                    option_new.rect.setRight(widget.width())
                option = option_new
            super().drawPrimitive(element, option, painter, widget)

    class ExportModel(QtCore.QAbstractTableModel):
        def __init__(self, controller):
            QtCore.QAbstractTableModel.__init__(self)
            self.controller = controller
            self.data = controller.exports

        def rowCount(self, parent):
            return len(self.data)

        def columnCount(self, parent):
            return 1

        def headerData(self, section, orientation, role):
            if role == QtCore.Qt.DisplayRole:
                if orientation == QtCore.Qt.Horizontal:
                    return ["Export"][section]
                if orientation == QtCore.Qt.Vertical:
                    return str(section+1)

        def data(self, index, role):
            if not index.isValid():
                return None
            if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
                r = index.row()
                c = index.column()
                return self.data[r][c]

        def flags(self, index):
            flags = QtCore.QAbstractTableModel.flags(self, index)
            if index.isValid():
                flags = flags | QtCore.Qt.ItemIsDragEnabled
            else:
                flags = flags | QtCore.Qt.ItemIsDropEnabled
            return flags

        def supportedDropActions(self):
            return QtCore.Qt.MoveAction

        def mimeTypes(self):
            return ["application/vnd.text.list"]

        def mimeData(self, index):
            r = index[0].row()
            d = QtCore.QMimeData()
            d.setData("application/vnd.text.list", json.dumps(self.data[r]).encode("utf-8"))
            return d

        def dropMimeData(self, data, action, row, column, parent):
            if row < 0:
                return False

            data = json.loads(bytes(data.data("application/vnd.text.list")).decode("utf-8"))
            self.beginInsertRows(QtCore.QModelIndex(), row, row)
            self.data.insert(row, data)
            self.endInsertRows()

            return True

        def removeRows(self, row, column, index):
            self.beginRemoveRows(QtCore.QModelIndex(), row, row)
            self.data.pop(row)
            self.endRemoveRows()

            self.controller.commit()
            return True

        def addEntry(self, export):
            row = len(self.data)
            self.beginInsertRows(QtCore.QModelIndex(), row, row)
            self.data.insert(row, export)
            self.endInsertRows()

        def removeEntry(self, row):
            self.beginRemoveRows(QtCore.QModelIndex(), row, row)
            self.data.pop(row)
            self.endRemoveRows()

    progress_signal = pyqtSignal(int, int, int, bool)

    def __init__(self, ui):
        QtCore.QObject.__init__(self)
        self.ui = ui
        self.ui.uiref["export_dialog"] = self

        self.exports = list(self.ui.core.exports)

        self.exportui = uic.loadUi(os.path.join(ui.app_path, "exportDialog.ui"))

        self.splitter = self.exportui.findChild(QSplitter, "splitter")
        self.splitter.setSizes([200, 1])
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        # Table
        self.table_export = self.exportui.findChild(QTableView, "table_export")
        self.table_export.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_export.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_export.setDragDropMode(QAbstractItemView.InternalMove)
        self.table_export.setDragEnabled(True)
        self.table_export.setDropIndicatorShown(True)
        self.table_export.setDragDropOverwriteMode(False)

        self.model_export = self.ExportModel(self)
        self.table_export.setModel(self.model_export)
        self.table_export.setStyle(self.TableStyle())

        self.table_export.selectionModel().selectionChanged.connect(self.onSelectionChanged)

        header = self.table_export.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        # Load/Save
        self.edit_export = self.exportui.findChild(QLineEdit, "edit_export")
        self.btn_load = self.exportui.findChild(QPushButton, "btn_load")
        self.btn_load.clicked.connect(self.onLoad)
        self.btn_save = self.exportui.findChild(QPushButton, "btn_save")
        self.btn_save.clicked.connect(self.onSave)

        # Edit
        self.edit_filter = self.exportui.findChild(QLineEdit, "edit_filter")
        self.edit_filter.setText("%{COUNT}==0")

        self.edit_outputdir = self.exportui.findChild(QLineEdit, "edit_outputdir")
        self.chk_overwrite = self.exportui.findChild(QCheckBox, "overwrite")
        self.btn_browse = self.exportui.findChild(QToolButton, "btn_browse")
        self.btn_browse.clicked.connect(self.onBrowse)

        self.edit_filename = self.exportui.findChild(QLineEdit, "edit_filename")
        self.edit_filename.setText("""PREFIX(BASENAME(%{FILE}))+"#"+%{PAGE}+"-"+%{LEVEL}+"-"+%{INDEX}+"."+%{EXTENSION}""")

        self.edit_content = QAutoEdit()
        self.edit_content.setPlainText("%{CONTENT}")
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

    @QtCore.pyqtSlot(QtCore.QItemSelection, QtCore.QItemSelection)
    def onSelectionChanged(self, selected, deselected):
        fn = self.exports[self.table_export.selectionModel().selectedRows()[0].row()][0]
        self.edit_export.setText(fn)

    def onBrowse(self):
        outputdir = QFileDialog.getExistingDirectory(self.exportui, u"Select Output Directory")
        if outputdir:
            self.edit_outputdir.setText(outputdir)


    def onLoad(self):
        exports = self.edit_export.text()
        for d in self.exports:
            if d[0] == exports:
                filter = d[1]["filter"]
                outputdir = d[1]["outputdir"]
                filename = d[1]["filename"]
                content = d[1]["content"]
                overwrite = d[1].get("overwrite", True)
                break
        else:
            filter = ""
            outputdir = ""
            filename = ""
            content = ""
            overwrite = True
        self.edit_filter.setText(filter)
        self.edit_outputdir.setText(outputdir)
        self.edit_filename.setText(filename)
        self.edit_content.setPlainText(content)
        self.chk_overwrite.setChecked(overwrite)

    def onSave(self):
        exports = self.edit_export.text()
        data = {
            "filter": self.edit_filter.text(),
            "outputdir": self.edit_outputdir.text(),
            "filename": self.edit_filename.text(),
            "content": self.edit_content.toPlainText(),
            "overwrite": self.chk_overwrite.isChecked()
        }
        changed = False
        for d in self.exports:
            if d[0] == exports:
                ret = QMessageBox.question(self.exportui, 'Save Export', "Overwrite?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if ret == QMessageBox.Yes:
                    d[1] = data
                    changed = True
                break
        else:
            self.model_export.addEntry([exports, data])
            changed = True
        if changed:
            self.commit()

    def onApply(self):
        self.message.setText("Exporting...")
        self.ui.core.worker.addFgJob(self)

    def __call__(self):
        self.handler = JobHandler()
        filter = self.edit_filter.text()
        outputdir = self.edit_outputdir.text()
        filename = self.edit_filename.text()
        content = self.edit_content.toPlainText()
        overwrite = self.chk_overwrite.isChecked()
        self.ui.core.export(filter, outputdir, filename, content, overwrite, self.handler, self.onProgress)

    def onProgress(self, done, total, exported, finished):
        self.progress_signal.emit(done, total, exported, finished)

    def _onProgress(self, done, total, exported, finished):
        if finished:
            if self.progress_dialog and not self.progress_dialog.wasCanceled():
                self.progress_dialog.hide()
            self.progress_dialog = None
            self.message.setText("Export finished at {}".format(datetime.now()))
        else:
            if self.progress_dialog is None:
                self.progress_dialog = QProgressDialog("Exporting...", "Abort", done, total, self.exportui)
                self.progress_dialog.canceled.connect(self.abort)
                self.progress_dialog.setAutoReset(False)
                self.progress_dialog.setAutoClose(False)
                self.progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
                self.progress_dialog.show()
                time.sleep(0.05)
            self.progress_dialog.setValue(done)
            self.progress_dialog.setLabelText("Exporting... ({} exported)".format(exported))

    def abort(self):
        self.handler.cancel()

    def onClose(self):
        self.exportui.close()
        self.ui.uiref.pop("export_dialog", None)

    def commit(self):
        self.ui.core.updateExports(self.exports)