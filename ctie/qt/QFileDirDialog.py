import os
from PySide import QtGui

class QFileDirDialog(QtGui.QFileDialog):
	def __init__(self):
		super(self.__class__, self).__init__()
		self.selected = []
		self. m_btnOpen = None
		self.setOption(QtGui.QFileDialog.ShowDirsOnly, False)
		self.setOption(QtGui.QFileDialog.DontUseNativeDialog, True)

		for btn in self.findChildren(QtGui.QPushButton):
			text = btn.text().lower()
			if text.find("open") != -1 or text.find("choose") != -1:
				self.m_btnOpen = btn
				break

		self.m_btnOpen.clicked.disconnect()
		self.m_btnOpen.clicked.connect(self.open)

		self.listView = self.findChild(QtGui.QListView, "listView")
		if self.listView:
			self.listView.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
		l = self.findChild(QtGui.QTreeView)
		if l:
			l.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)

	def open(self):
		self.selected = []
		for index in self.listView.selectionModel().selectedIndexes():
			if index.column()==0:
				self.selected.append(os.path.join(self.directory().absolutePath(), index.data()))
		self.close()

	def selectedFiles(self):
		return self.selected
