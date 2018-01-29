import math
from utils import *
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QWidget

class WorkArea():
	class QWorkArea(QWidget):
		scale = 1
		item = None
		selstart = (None, None)
		selend = (None, None)
		mode = None

		def mousePressEvent(self, event):
			x = event.x()/self.scale
			y = event.y()/self.scale
			self.selstart = (x, y)
			self.selend = (x, y)
			if not len(self.ui.core.selections):
				self.mode = 'rect'
			else:
				for i in self.ui.core.selections:
					child = self.item.children[i]
					if child.contains(x+self.item.x1, y+self.item.y1):
						self.mode = 'move'
						break
				else:
					self.mode = 'resize'
			self.update()

		def mouseMoveEvent(self, event):
			self.selend = (event.x()/self.scale, event.y()/self.scale)
			self.update()

		def mouseReleaseEvent(self, event):
			item = self.item
			x2 = event.x()/self.scale
			y2 = event.y()/self.scale
			if False:
				pass
			else:
				x1,y1 = self.selstart
				if (x1,y1)==(None, None):
					return

				xoff = x2-x1
				yoff = y2-y1
				r = math.sqrt(xoff**2+yoff**2)
				if r<5:
					for i, child in enumerate(self.item.children):
						if child.contains(x2+self.item.x1, y2+self.item.y1):
							if i in self.ui.core.selections:
								self.ui.core.deselectChildByIndex(i)
							else:
								self.ui.core.selectChildByIndex(i)
				elif self.mode=='rect':
					x1, x2 = asc(x1, x2)
					y1, y2 = asc(y1, y2)
					x1 = max(x1, 0)
					y1 = max(y1, 0)
					x2 = min(x2, self.item.x2-self.item.x1)
					y2 = min(y2, self.item.y2-self.item.y1)
					if x2-x1>5 and y2-y1>5:
						self.item.addChild(x1 = x1+self.item.x1, y1 = y1+self.item.y1, x2 = x2+self.item.x1, y2 = y2+self.item.y1)
				elif self.mode=='move':
					xoff = self.selend[0]-self.selstart[0]
					yoff = self.selend[1]-self.selstart[1]
					self.ui.core.move(xoff, yoff)
				elif self.mode=='resize':
					xoff = self.selend[0]-self.selstart[0]
					yoff = self.selend[1]-self.selstart[1]
					self.ui.core.resize(xoff, yoff)
			self.selstart = (None, None)
			self.selend = (None, None)
			self.mode = None
			self.update()

		def wheelEvent(self, event):
			self.scale += event.angleDelta().y()/4096
			self.scale = min(self.scale, 10)
			self.scale = max(self.scale, 0.03)
			self.setGeometry(0, 0, self.w*self.scale, self.h*self.scale)
			self.update()

		def paintEvent(self, event):
			if not self.item:
				return
			item = self.item
			painter = QtGui.QPainter(self)
			painter.scale(self.scale, self.scale)
			item.drawQT(painter)

			if self.selstart!=(None, None) and self.selend!=(None, None):
				sx0, sy0 = self.selstart
				sx1, sy1 = self.selend
				xoff = sx1 - sx0
				yoff = sy1 - sy0

				if len(self.ui.core.selections)==0: # new rect
					painter.setPen(QtGui.QPen(QtCore.Qt.blue, 1/self.scale, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
					painter.drawRect(sx0,sy0,xoff,yoff)
			else:
				xoff = 0
				yoff = 0

			pen = QtGui.QPen(QtCore.Qt.red, 1/self.scale, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap)
			painter.setPen(pen)
			for i, child in enumerate(item.children):
				x1 = (child.x1-item.x1)
				y1 = (child.y1-item.y1)
				x2 = (child.x2-item.x1)
				y2 = (child.y2-item.y1)
				if i in self.ui.core.selections:
					pen.setColor(QtCore.Qt.blue)
					painter.setPen(pen)
					if self.mode=='move':
						painter.drawRect(x1+xoff, y1+yoff, x2-x1, y2-y1)
					elif self.mode=='resize':
						ex1, ex2 = asc(x1, x2+xoff)
						ey1, ey2 = asc(y1, y2+yoff)
						painter.drawRect(ex1, ey1, ex2-ex1, ey2-ey1)
					else:
						painter.drawRect(x1, y1, x2-x1, y2-y1)
				else:
					pen.setColor(QtCore.Qt.red)
					painter.setPen(pen)
					painter.drawRect(x1, y1, x2-x1, y2-y1)

		def resizeEvent(self, event):
			pass

		def onItemChanged(self):
			self.item = self.ui.core.getCurrentItem()
			if not self.item:
				return
			self.w, self.h = self.item.getSize()
			self.setGeometry(0, 0, self.w*self.scale, self.h*self.scale)

	def __init__(self, ui, workAreaScroller):
		self.ui = ui
		self.workAreaScroller = workAreaScroller
		self.workArea = self.QWorkArea()
		# self.workArea.setSizePolicy(QtGui.QSizePolicy.Policy.Ignored, QtGui.QSizePolicy.Policy.Ignored)
		self.workArea.ui = ui
		self.workAreaScroller.setWidget(self.workArea)

	def onItemChanged(self):
		self.workArea.onItemChanged()
