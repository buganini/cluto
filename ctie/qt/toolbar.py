from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from .QChrootFileDirDialog import *

class Toolbar():
    def __init__(self, ui, toolBar):
        self.ui = ui

        # http://drive.noobslab.com/data/themes/gimp/flat-themes.tar.gz
        resourcePath = os.path.join(os.path.dirname(__file__), "..", "icons")

        self.tbProject = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-open.png")), "&Project")
        self.tbLoad = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-open.png")), "&Load")
        self.tbSave = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-save.png")), "&Save")

        self.tbProject.triggered.connect(self.openProject)
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

        self.tbZoomIn = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-zoom-in.png")), "Zoom In")
        self.tbZoomOut = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-zoom-out.png")), "Zoom Out")
        self.tbZoomActual = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-zoom-100.png")), "Zoom 100%")
        self.tbZoomFit = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-zoom-fit.png")), "Zoom Fit")

        toolBar.addSeparator()

        self.tbCopy = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-duplicate-16.png")), "Copy")
        self.tbCopySetting = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-preferences.png")), "Copy Setting")
        self.tbPaste = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-paste.png")), "Paste")

        self.tbCopy.triggered.connect(self.copy)
        self.tbPaste.triggered.connect(self.paste)

        toolBar.addSeparator()

        self.tbDeleteSelection = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-delete.png")), "Delete Selection Area(s)")
        self.tbResetChildrenOrder = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-reset-16.png")), "Reset Children Order")

        self.tbDeleteSelection.triggered.connect(self.deleteSelectedChildren)

        toolBar.addSeparator()

        self.tbHorizontalSplitter = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-flip-horizontal-16.png")), "Horizontal Splitter")
        self.tbVerticalSplitter = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-flip-vertical-16.png")), "Vertical Splitter")
        self.tbTableRowSplitter = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-gravity-west-16.png")), "Table Row Splitter")
        self.tbTableColumnSplitter = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-gravity-south-16.png")), "Table Column Splitter")

        toolBar.addSeparator()

        self.tbItemFolder = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-cursor-c16.png")), "Open working folder of current item")

        self.tbItemFolder.triggered.connect(self.itemFolder)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolBar.addWidget(spacer)

        self.tbExport = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-revert-to-saved-ltr.png")), "Export")
        self.tbDisplayAreaPath = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-vchain-16.png")), "Display Area(s) Path")
        self.tbOcrMode = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-bold.png")), "OCR Mode")
        self.tbCollationMode = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-edit.png")), "Collation Mode")

        self.tbDisplayAreaPath.setCheckable(True)
        self.tbOcrMode.setCheckable(True)
        self.tbCollationMode.setCheckable(True)

        self.tbOcrMode.toggled.connect(self.toggleOcrMode)
        self.tbCollationMode.toggled.connect(self.toggleCollationMode)

        self.tbLoad.setEnabled(False)
        self.tbSave.setEnabled(False)
        self.tbAddFiles.setEnabled(False)
        self.tbAddFolder.setEnabled(False)
        self.tbDelete.setEnabled(False)

    def onProjectChanged(self):
        self.tbLoad.setEnabled(True)
        self.tbSave.setEnabled(True)
        self.tbAddFiles.setEnabled(True)
        self.tbAddFolder.setEnabled(True)
        self.tbDelete.setEnabled(True)

    def openProject(self):
        self.ui.openProject()

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

    def copy(self):
        self.ui.core.copy()

    def paste(self):
        self.ui.core.paste()

    def deleteSelectedChildren(self):
        self.ui.core.deleteSelectedChildren()

    def itemFolder(self):
        item = self.ui.core.getCurrentItem()
        if item is None:
            return
        self.ui.utils.open_path(item.getWorkdir())

    def toggleOcrMode(self, enabled):
        self.ui.core.setOcrMode(enabled)

    def toggleCollationMode(self, enabled):
        self.ui.core.setCollationMode(enabled)