from PySide import QtGui
from QFileDirDialog import *

class Toolbar():
	def __init__(self, ui, toolBar):
		self.ui = ui

		# http://drive.noobslab.com/data/themes/gimp/flat-themes.tar.gz
		resourcePath = os.path.join(os.path.dirname(__file__), "..", "icons")

		tbOpen = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-open.png")), "&Open")
		tbSave = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-save.png")), "&Save")
		toolBar.addSeparator()
		tbAdd = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-add.png")), "&Add")
		tbDelete = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-remove.png")), "&Delete")
		toolBar.addSeparator()
		tbZoomIn = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-zoom-in.png")), "Zoom In")
		tbZoomOut = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-zoom-out.png")), "Zoom Out")
		tbZoomActual = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-zoom-100.png")), "Zoom 100%")
		tbZoomFit = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-zoom-fit.png")), "Zoom Fit")
		toolBar.addSeparator()
		tbRegex = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-tool-flip-16.png")), "Regex")
		tbCopy = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-duplicate-16.png")), "Copy")
		tbCopySetting = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-preferences.png")), "Copy Setting")
		tbPaste = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-paste.png")), "Paste")
		tbAutoPaste = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-plugin-16.png")), "Auto Paste")
		toolBar.addSeparator()
		tbDeleteSelection = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-delete.png")), "Delete Selection Area(s)")
		tbResetChildrenOrder = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-reset-16.png")), "Reset Children Order")
		toolBar.addSeparator()
		tbHorizontalSplitter = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-flip-horizontal-16.png")), "Horizontal Splitter")
		tbVerticalSplitter = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-flip-vertical-16.png")), "Vertical Splitter")
		tbTableRowSplitter = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-gravity-west-16.png")), "Table Row Splitter")
		tbTableColumnSplitter = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-gravity-south-16.png")), "Table Column Splitter")
		spacer = QtGui.QWidget()
		spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
		toolBar.addWidget(spacer)
		tbExport = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-revert-to-saved-ltr.png")), "Export")
		tbDisplayAreaPath = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "stock-vchain-16.png")), "Display Area(s) Path")
		tbOcrMode = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-bold.png")), "OCR Mode")
		tbCollationMode = toolBar.addAction(QtGui.QIcon(os.path.join(resourcePath, "gtk-edit.png")), "Collation Mode")

		tbOpen.triggered.connect(self.open)
		tbAdd.triggered.connect(self.add)

	def open(self):
		dialog = QtGui.QFileDialog()
		dialog.exec_()

	def add(self):
		dialog = QFileDirDialog()
		dialog.run()
		for path in dialog.selectedFiles():
			self.ui.core.addItemByPath(path)
