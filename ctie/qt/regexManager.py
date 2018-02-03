from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import uic
import os
import json
import re

class RegexManager(QtCore.QObject):
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

    class RegularExpressionTableModel(QtCore.QAbstractTableModel):
        def __init__(self, data):
            QtCore.QAbstractTableModel.__init__(self)
            self.data = data

        def rowCount(self, parent):
            return len(self.data)

        def columnCount(self, parent):
            return 2

        def headerData(self, section, orientation, role):
            if role == QtCore.Qt.DisplayRole:
                if orientation == QtCore.Qt.Horizontal:
                    return ["Pattern", "Replacement"][section]
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
                flags = flags | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled
            else:
                flags = flags | QtCore.Qt.ItemIsDropEnabled
            return flags

        def setData(self, index, value, role=QtCore.Qt.EditRole):
            if role == QtCore.Qt.EditRole:
                r = index.row()
                c = index.column()
                self.data[r][c] = value
            return True

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

            return True

        def addEntry(self):
            row = len(self.data)
            self.beginInsertRows(QtCore.QModelIndex(), row, row)
            self.data.insert(row, ["", ""])
            self.endInsertRows()

        def removeEntry(self, row):
            self.beginRemoveRows(QtCore.QModelIndex(), row, row)            
            self.data.pop(row)
            self.endRemoveRows()

    class CheckTableTableModel(QtCore.QAbstractTableModel):
        def __init__(self, data, diff):
            QtCore.QAbstractTableModel.__init__(self)
            self.data = data
            self.diff = diff

        def rowCount(self, parent):
            return len(self.data)

        def columnCount(self, parent):
            return 3

        def headerData(self, section, orientation, role):
            if role == QtCore.Qt.DisplayRole:
                if orientation == QtCore.Qt.Horizontal:
                    return ["Input", "Output", "E/Result"][section]

        def data(self, index, role):
            if not index.isValid():
                return None
            if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
                r = index.row()
                c = index.column()
                if c < 2:
                    return self.data[r][c]
                else:
                    return self.diff[r]

        def flags(self, index):
            flags = QtCore.QAbstractTableModel.flags(self, index)
            c = index.column()
            if c < 2:
                flags = flags | QtCore.Qt.ItemIsEditable
            return flags

        def setData(self, index, value, role=QtCore.Qt.EditRole):
            if role == QtCore.Qt.EditRole:
                r = index.row()
                c = index.column()
                self.data[r][c] = value
            return True

        def addEntry(self):
            row = len(self.data)
            self.beginInsertRows(QtCore.QModelIndex(), row, row)
            self.data.insert(row, ["", ""])
            self.diff.insert(row, "")
            self.endInsertRows()

        def removeEntry(self, row):
            self.beginRemoveRows(QtCore.QModelIndex(), row, row)            
            self.data.pop(row)
            self.diff.pop(row)
            self.endRemoveRows()

    def __init__(self, ui):
        QtCore.QObject.__init__(self)
        self.ui = ui
        self.ui.uiref["regex_manager"] = self

        self.regex = list(self.ui.core.regex)
        self.tests = list(self.ui.core.tests)
        self.diff = [""] * len(self.tests)

        self.regexui = uic.loadUi(os.path.join(ui.app_path, "regexManager.ui"))

        # Regular Expression
        self.regular_expression = self.regexui.findChild(QTableView, "regular_expression")
        self.regular_expression.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.regular_expression.setSelectionMode(QAbstractItemView.SingleSelection)
        self.regular_expression.setDragDropMode(QAbstractItemView.InternalMove)
        self.regular_expression.setDragEnabled(True)
        self.regular_expression.setDropIndicatorShown(True)
        self.regular_expression.setDragDropOverwriteMode(False)

        self.model_regular_expression = self.RegularExpressionTableModel(self.regex)
        self.regular_expression.setModel(self.model_regular_expression)
        self.regular_expression.setStyle(self.TableStyle())

        header = self.regular_expression.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        self.btn_remove_regex = self.regexui.findChild(QToolButton, "btn_remove_regex")
        self.btn_remove_regex.clicked.connect(self.onBtnRemoveRegex)
        self.btn_add_regex = self.regexui.findChild(QToolButton, "btn_add_regex")
        self.btn_add_regex.clicked.connect(self.onBtnAddRegex)

        # Check Table
        self.check_table = self.regexui.findChild(QTableView, "check_table")
        self.check_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.check_table.setSelectionMode(QAbstractItemView.SingleSelection)

        self.model_check_table = self.CheckTableTableModel(self.tests, self.diff)
        self.check_table.setModel(self.model_check_table)

        header = self.check_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        self.btn_remove_test = self.regexui.findChild(QToolButton, "btn_remove_test")
        self.btn_remove_test.clicked.connect(self.onBtnRemoveTest)
        self.btn_add_test = self.regexui.findChild(QToolButton, "btn_add_test")
        self.btn_add_test.clicked.connect(self.onBtnAddTest)
        self.btn_check = self.regexui.findChild(QPushButton, "btn_check")
        self.btn_check.clicked.connect(self.onBtnCheck)

        # Message
        self.message = self.regexui.findChild(QLabel, "message")

        # Buttons
        self.buttons = self.regexui.findChild(QDialogButtonBox, "buttons")
        self.buttons.accepted.connect(self.onAccepted)
        self.buttons.rejected.connect(self.onRejected)

        self.regexui.show()

    def onBtnAddRegex(self):
        self.model_regular_expression.addEntry()
        self.regular_expression.scrollToBottom()

    def onBtnRemoveRegex(self):
        rows = self.regular_expression.selectionModel().selectedRows()
        if not rows:
            return
        self.model_regular_expression.removeEntry(rows[0].row())

    def onBtnAddTest(self):
        self.model_check_table.addEntry()
        self.check_table.scrollToBottom()

    def onBtnRemoveTest(self):
        rows = self.check_table.selectionModel().selectedRows()
        if not rows:
            return
        self.model_check_table.removeEntry(rows[0].row())

    def onBtnCheck(self):
        self.message.setText("")
        try:
            for i in range(len(self.tests)):
                text = self.tests[i][0]
                expected = self.tests[i][1]
                for j in range(len(self.regex)):
                    reg = self.regex[j][0]
                    rep = self.regex[j][1]
                    try:
                        text = re.sub(reg, rep, text)
                    except Exception as e:
                        msg = "Regex error at {}: {}".format(j+1, e)
                        self.message.setText(msg)
                        raise Exception()
                if expected == text:
                    self.diff[i] = ""
                else:
                    self.diff[i] = text
        except Exception as e:
            pass
        self.model_check_table.dataChanged.emit(self.model_check_table.index(0, 2), self.model_check_table.index(len(self.diff)-1, 2), [QtCore.Qt.DisplayRole])

    @QtCore.pyqtSlot()
    def onAccepted(self):
        self.ui.core.updateRegex(self.regex, self.tests)
        self.close()

    @QtCore.pyqtSlot()
    def onRejected(self):
        self.close()

    def close(self):
        self.regexui.close()
        self.ui.uiref.pop("regex_manager", None)