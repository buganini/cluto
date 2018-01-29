import os
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import *

class ItemList(QObject):
	class QClickableWidget(QWidget):
		clicked = pyqtSignal(QWidget)

		def mouseReleaseEvent(self, *args):
			self.clicked.emit(self)

	def __init__(self, ui, listView, scroller):
		QObject.__init__(self)
		self.ui = ui
		self.listView = listView
		self.scroller = scroller

	def scrollTo(self, widget):
		self.scroller.ensureWidgetVisible(widget, 0, 50)

	def reset(self):
		for i in reversed(range(self.listView.count())):
			self.listView.itemAt(i).widget().deleteLater()
		currentItem = self.ui.core.getCurrentItem()
		for item in self.ui.core.items:
			layout = QVBoxLayout()
			layout.setSpacing(0)

			img = QLabel()
			img.setStyleSheet("padding: 10px;")
			img.setAlignment(QtCore.Qt.AlignCenter)
			item.drawThumbnailQT(img, 300, 200)
			layout.addWidget(img)

			label = QLabel()
			label.setStyleSheet("padding: 10px;")
			label.setAlignment(QtCore.Qt.AlignCenter)
			label.setText(os.path.basename(item.path))
			layout.addWidget(label)

			widget = self.QClickableWidget()
			widget.setLayout(layout)
			widget.item = item
			widget.clicked.connect(self.onItemSelected)

			item.ui = widget

			if item == currentItem:
				item.ui.setStyleSheet("background-color:rgba(50,50,255,30);");

			self.listView.addWidget(widget)


	@pyqtSlot(QWidget)
	def onItemSelected(self, widget):
		self.ui.core.selectItemByIndex(widget.item.getIndex())
