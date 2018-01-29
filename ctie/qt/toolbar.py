from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from .QChrootFileDirDialog import *

class Toolbar():
    def __init__(self, ui, toolBar):
        self.ui = ui

        # http://drive.noobslab.com/data/themes/gimp/flat-themes.tar.gz
        resourcePath = os.path.join(os.path.dirname(__file__), "..", "icons")

        self.tbProject = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-open.png")), "&Project")
        self.tbOpen = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-open.png")), "&Open")
        self.tbSave = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-save.png")), "&Save")
        toolBar.addSeparator()
        self.tbAddFiles = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-add.png")), "&Add Files")
        self.tbAddFolder = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-add.png")), "&Add Folder")
        self.tbDelete = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-remove.png")), "&Delete")
        toolBar.addSeparator()
        self.tbZoomIn = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-zoom-in.png")), "Zoom In")
        self.tbZoomOut = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-zoom-out.png")), "Zoom Out")
        self.tbZoomActual = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-zoom-100.png")), "Zoom 100%")
        self.tbZoomFit = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-zoom-fit.png")), "Zoom Fit")
        toolBar.addSeparator()
        self.tbRegex = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-tool-flip-16.png")), "Regex")
        self.tbCopy = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-duplicate-16.png")), "Copy")
        self.tbCopySetting = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-preferences.png")), "Copy Setting")
        self.tbPaste = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-paste.png")), "Paste")
        self.tbAutoPaste = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-plugin-16.png")), "Auto Paste")
        toolBar.addSeparator()
        self.tbDeleteSelection = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-delete.png")), "Delete Selection Area(s)")
        self.tbResetChildrenOrder = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-reset-16.png")), "Reset Children Order")
        toolBar.addSeparator()
        self.tbHorizontalSplitter = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-flip-horizontal-16.png")), "Horizontal Splitter")
        self.tbVerticalSplitter = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-flip-vertical-16.png")), "Vertical Splitter")
        self.tbTableRowSplitter = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-gravity-west-16.png")), "Table Row Splitter")
        self.tbTableColumnSplitter = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-gravity-south-16.png")), "Table Column Splitter")
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolBar.addWidget(spacer)
        self.tbExport = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-revert-to-saved-ltr.png")), "Export")
        self.tbDisplayAreaPath = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-vchain-16.png")), "Display Area(s) Path")
        self.tbOcrMode = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-bold.png")), "OCR Mode")
        self.tbCollationMode = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-edit.png")), "Collation Mode")

        self.tbProject.triggered.connect(self.openProject)
        self.tbOpen.triggered.connect(self.open)
        self.tbAddFiles.triggered.connect(self.addFiles)
        self.tbAddFolder.triggered.connect(self.addFolder)

        self.tbOpen.setEnabled(False)
        self.tbSave.setEnabled(False)
        self.tbAddFiles.setEnabled(False)
        self.tbAddFolder.setEnabled(False)

    def onProjectChanged(self):
        self.tbOpen.setEnabled(True)
        self.tbSave.setEnabled(True)
        self.tbAddFiles.setEnabled(True)
        self.tbAddFolder.setEnabled(True)

    def openProject(self):
        project = QFileDialog.getExistingDirectory(None, u"Select Project Folder")
        self.ui.core.openProject(project)

    def open(self):
        dialog = QtGui.QFileDialog()
        dialog.exec_()

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
