import os
from PySide import QtGui, QtCore

class ItemList():
	class QClickableWidget(QtGui.QWidget):
		clicked = QtCore.Signal(QtGui.QWidget)

		def mouseReleaseEvent(self, *args):
			self.clicked.emit(self)

	def __init__(self, ui, listView):
		this = self
		self.ui = ui
		self.listView = listView

	def reset(self):
		for i in reversed(range(self.listView.count())):
			self.listView.itemAt(i).widget().deleteLater()
		for item in self.ui.ctie.items:
			layout = QtGui.QVBoxLayout()
			layout.setSpacing(0)

			img = QtGui.QLabel()
			img.setStyleSheet("padding: 10px;")
			img.setAlignment(QtCore.Qt.AlignCenter)
			item.drawThumbnailQT(img, 300, 200)
			layout.addWidget(img)

			label = QtGui.QLabel()
			label.setStyleSheet("padding: 10px;")
			label.setAlignment(QtCore.Qt.AlignCenter)
			label.setText(os.path.basename(item.path))
			layout.addWidget(label)

			widget = self.QClickableWidget()
			widget.setLayout(layout)
			widget.item = item
			widget.clicked.connect(self.onItemSelected)

			item.ui = widget

			self.listView.addWidget(widget)


	@QtCore.Slot(QtGui.QWidget)
	def onItemSelected(self, widget):
		self.ui.ctie.selectItemByIndex(widget.item.getIndex())
