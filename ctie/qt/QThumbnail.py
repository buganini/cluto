from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *

class QThumbnail(QWidget):
    th_width = 300
    th_height = 200

    def __init__(self, item):
        QWidget.__init__(self)
        self.item = item
        self.w = item.x2 - item.x1
        self.h = item.y2 - item.y1
        xscale = self.th_width / self.w
        yscale = self.th_height / self.h
        self.scale = min(xscale, yscale)
        self.setFixedSize(self.w*self.scale, self.h*self.scale)

    def paintEvent(self, event):
        item = self.item
        painter = QtGui.QPainter(self)
        painter.scale(self.scale, self.scale)
        item.drawQT(painter)