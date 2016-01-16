import os
from PySide import QtGui, QtCore

class ItemList():
	class Delegate(QtGui.QItemDelegate):
		def __init__(self, ctie):
			super(self.__class__, self).__init__()
			self.ctie = ctie
			self.layout = QtGui.QVBoxLayout()
			self.img = QtGui.QLabel()
			self.label = QtGui.QLabel()
			self.layout.addWidget(self.img)
			self.layout.addWidget(self.label)
			self.view = QtGui.QWidget()
			self.view.setLayout(self.layout)

		def paint(self, painter, option, index):
			pic = QtGui.QPixmap(option.rect.width(), option.rect.height())
			self.view.setGeometry(option.rect)

			item = self.ctie.items[index.row()]

			self.img.setScaledContents(True)
			item.drawThumbnailQT(self.img, option.rect.width(), option.rect.height()-20)

			self.label.setText(os.path.basename(self.ctie.items[index.row()].path))
			self.view.render(pic)
			painter.drawPixmap(option.rect, pic)

		def sizeHint(self, option, index):
			ls = self.label.sizeHint()
			s = QtCore.QSize()
			s.setWidth(ls.width())
			s.setHeight(ls.height()+300)
			return s

	class Model(QtCore.QAbstractListModel):
		def __init__(self, ctie):
			super(self.__class__, self).__init__()
			self.ctie = ctie

		def rowCount(self, parent = QtCore.QModelIndex()):
			return len(self.ctie.items)

		def data(self, index, role = QtCore.Qt.DisplayRole):
			if role == QtCore.Qt.DisplayRole:
				return "123"

	def __init__(self, ui, listView):
		this = self
		self.ui = ui
		self.listView = listView

		self.model = self.Model(self.ui.ctie)
		self.delegate = self.Delegate(self.ui.ctie)
		listView.setItemDelegate(self.delegate)

	def reset(self):
		self.listView.setModel(None)
		self.listView.setModel(self.model)
		self.listViewSelectionModel = self.listView.selectionModel()
		self.listViewSelectionModel.currentChanged.connect(self.onItemSelected)

	def onItemSelected(self, currIndex, prevIndex):
		self.ui.ctie.selectItemByIndex(currIndex.row())
