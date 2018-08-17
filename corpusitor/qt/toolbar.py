from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from .QChrootFileDirDialog import *
from .copySettingsDialog import *
from .exportDialog import *

class Toolbar():
    def __init__(self, ui, toolBar):
        self.ui = ui

        # http://drive.noobslab.com/data/themes/gimp/flat-themes.tar.gz
        resourcePath = os.path.join(os.path.dirname(__file__), "..", "icons")

        self.tbLoad = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-open.png")), "&Load")
        self.tbSave = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-save.png")), "&Save")

        self.tbLoad.triggered.connect(self.load)
        self.tbSave.triggered.connect(self.save)

        toolBar.addSeparator()
        self.tbAddFiles = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-add.png")), "&Add Files")
        self.tbAddFolder = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-add.png")), "&Add Folder")
        self.tbDelete = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-remove.png")), "&Delete")

        self.tbAddFiles.triggered.connect(self.addFiles)
        self.tbAddFolder.triggered.connect(self.addFolder)
        self.tbDelete.triggered.connect(self.deleteItem)

        toolBar.addSeparator()

        self.tbZoomActual = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-zoom-100.png")), "Zoom 100%")
        self.tbZoomFit = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-zoom-fit.png")), "Zoom Fit")

        self.tbZoomActual.triggered.connect(self.zoomActual)
        self.tbZoomFit.triggered.connect(self.zoomFit)

        toolBar.addSeparator()

        self.tbCopy = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-duplicate-16.png")), "Copy")
        self.tbCopySettings = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-preferences.png")), "Copy Settings")
        self.tbPaste = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-paste.png")), "Paste")

        self.tbCopy.triggered.connect(self.copy)
        self.tbCopySettings.triggered.connect(self.copy_settings)
        self.tbPaste.triggered.connect(self.paste)

        toolBar.addSeparator()

        self.tbDeleteSelection = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-delete.png")), "Delete Selection Area(s)")
        self.tbResetChildrenOrder = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-reset-16.png")), "Reset Children Order")

        self.tbDeleteSelection.triggered.connect(self.deleteSelectedChildren)

        toolBar.addSeparator()

        self.tbHorizontalSplitter = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "horizontal_splitter.png")), "Horizontal Splitter")
        self.tbVerticalSplitter = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "vertical_splitter.png")), "Vertical Splitter")
        self.tbTableRowSplitter = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "table_row_splitter.png")), "Table Row Splitter")
        self.tbTableColumnSplitter = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "table_column_splitter.png")), "Table Column Splitter")

        self.tbHorizontalSplitter.setCheckable(True)
        self.tbVerticalSplitter.setCheckable(True)
        self.tbTableRowSplitter.setCheckable(True)
        self.tbTableColumnSplitter.setCheckable(True)

        self.tbHorizontalSplitter.toggled.connect(self.onSetHorizontalSplitter)
        self.tbVerticalSplitter.toggled.connect(self.onSetVerticalSplitter)
        self.tbTableRowSplitter.toggled.connect(self.onSetTableRowSplitter)
        self.tbTableColumnSplitter.toggled.connect(self.onSetTableColumnSplitter)

        toolBar.addSeparator()

        self.tbExport = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-color-triangle-16.png")), "Export")
        self.tbItemFolder = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-cursor-c16.png")), "Open working folder of current item")

        self.tbExport.triggered.connect(self.export)
        self.tbItemFolder.triggered.connect(self.itemFolder)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolBar.addWidget(spacer)

        self.tbDisplayAreaPath = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-vchain-16.png")), "Display Area(s) Path")
        self.tbOcrMode = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-bold.png")), "OCR Mode")
        self.tbCollationMode = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-edit.png")), "Collation Mode")

        self.tbDisplayAreaPath.setCheckable(True)
        self.tbOcrMode.setCheckable(True)
        self.tbCollationMode.setCheckable(True)

        self.tbOcrMode.toggled.connect(self.toggleOcrMode)
        self.tbCollationMode.toggled.connect(self.toggleCollationMode)

        self.tbSave.setEnabled(False)
        self.tbAddFiles.setEnabled(False)
        self.tbAddFolder.setEnabled(False)
        self.tbDelete.setEnabled(False)

    def onProjectChanged(self):
        self.tbSave.setEnabled(True)
        self.tbAddFiles.setEnabled(True)
        self.tbAddFolder.setEnabled(True)
        self.tbDelete.setEnabled(True)

    def load(self):
        self.ui.load()

    def save(self):
        self.ui.save()

    def addFolder(self):
        dialog = QChrootFileDirDialog(self.ui.core.workspace, False)
        if dialog.exec_():
            for path in dialog.selectedFiles():
                self.ui.core.addItemByPath(path)

    def addFiles(self):
        dialog = QChrootFileDirDialog(self.ui.core.workspace, True)
        if dialog.exec_():
            for path in dialog.selectedFiles():
                self.ui.core.addItemByPath(path)

    def deleteItem(self):
        ret = QMessageBox.question(self.ui.ui, 'Delete Item', "Are you sure to delete this item?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ret == QMessageBox.Yes:
            item = self.ui.core.getCurrentItem()
            if item:
                item.remove()

    def zoomActual(self):
        self.ui.zoomActual()

    def zoomFit(self):
        self.ui.zoomFit()

    def copy(self):
        self.ui.core.copy()

    def copy_settings(self):
        CopySettingsDialog(self.ui)

    def paste(self):
        self.ui.core.paste()

    def deleteSelectedChildren(self):
        self.ui.core.deleteSelectedChildren()

    def export(self):
        ExportDialog(self.ui)

    def itemFolder(self):
        item = self.ui.core.getCurrentItem()
        if item is None:
            return
        self.ui.core.open_path(item.getWorkdir())

    def onItemChanged(self):
        self.updateUI()

    def onContentChanged(self):
        self.updateUI()

    def updateUI(self):
        item = self.ui.core.getCurrentItem()
        if item is None:
            self.tbHorizontalSplitter.setChecked(False)
            self.tbVerticalSplitter.setChecked(False)
            self.tbTableRowSplitter.setChecked(False)
            self.tbTableColumnSplitter.setChecked(False)
            self.tbHorizontalSplitter.setEnabled(False)
            self.tbVerticalSplitter.setEnabled(False)
            self.tbTableRowSplitter.setEnabled(False)
            self.tbTableColumnSplitter.setEnabled(False)
            return
        self.tbHorizontalSplitter.setEnabled(True)
        self.tbVerticalSplitter.setEnabled(True)
        isTable = item.getType()=="Table"
        if not isTable:
            self.tbTableRowSplitter.setChecked(False)
            self.tbTableColumnSplitter.setChecked(False)
        self.tbTableRowSplitter.setEnabled(isTable)
        self.tbTableColumnSplitter.setEnabled(isTable)

    def onSetHorizontalSplitter(self, enable):
        self.ui.core.setHorizontalSplitter(enable)

    def onSetVerticalSplitter(self, enable):
        self.ui.core.setVerticalSplitter(enable)

    def onSetTableRowSplitter(self, enable):
        self.ui.core.setTableRowSplitter(enable)

    def onSetTableColumnSplitter(self, enable):
        self.ui.core.setTableColumnSplitter(enable)

    def setHorizontalSplitter(self, enable):
        self.tbHorizontalSplitter.setChecked(enable)

    def setVerticalSplitter(self, enable):
        self.tbVerticalSplitter.setChecked(enable)

    def setTableRowSplitter(self, enable):
        self.tbTableRowSplitter.setChecked(enable)

    def setTableColumnSplitter(self, enable):
        self.tbTableColumnSplitter.setChecked(enable)

    def toggleOcrMode(self, enabled):
        self.ui.core.setOcrMode(enabled)

    def toggleCollationMode(self, enabled):
        self.ui.core.setCollationMode(enabled)