from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *

class QThumbnail(QWidget):
    th_width = 270
    th_height = 180
    padding = 5

    def __init__(self, item):
        QWidget.__init__(self)
        self.item = item
        self.w = item.x2 - item.x1
        self.h = item.y2 - item.y1
        xscale = self.th_width / self.w
        yscale = self.th_height / self.h
        self.scale = min(xscale, yscale)
        self.setFixedSize(int(self.w*self.scale+self.padding*2), int(self.h*self.scale+self.padding*2))

    def paintEvent(self, event):
        QWidget.paintEvent(self, event)
        item = self.item
        painter = QtGui.QPainter(self)
        item.drawQT(painter, self.padding, self.padding, self.scale)