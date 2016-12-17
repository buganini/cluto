import os
from PySide import QtGui

class QFileDirDialog():
	def __init__(self):
		# super(self.__class__, self).__init__()
		self.selected = []
		# self.setOption(QtGui.QFileDialog.ShowDirsOnly, False)
		# self.setFileMode(QtGui.QFileDialog.ExistingFiles)

	def run(self):
		self.selected = QtGui.QFileDialog.getOpenFileNames(None, u"Open")[0]

	def selectedFiles(self):
		return self.selected
