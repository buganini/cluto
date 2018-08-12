import math
from utils import *
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *

class WorkArea():
    class QWorkArea(QWidget):
        def __init__(self, scrollArea):
            QWidget.__init__(self)
            self.setMouseTracking(True)
            self.scrollArea = scrollArea
            self.scale = 1
            self.w = None
            self.h = None
            self.item = None
            self.selstart = (None, None)
            self.selend = (None, None)
            self.mode = None

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
            coord = []
            if self.selstart[0]:
                coord.append("({:.2f}, {:.2f})".format(self.selstart[0], self.selstart[1]))
                coord.append(" - ")
                coord.append("({:.2f}, {:.2f})".format(self.selend[0], self.selend[1]))
                coord.append(" {:.2f} x {:.2f}".format(abs(self.selend[0] - self.selstart[0]), abs(self.selend[1] - self.selstart[1])))
            else:
                coord.append("({:.2f}, {:.2f})".format(self.selend[0], self.selend[1]))
            coord = "".join(coord)
            self.ui.set_status(coord)

        def mouseReleaseEvent(self, event):
            item = self.item
            x2 = event.x()/self.scale
            y2 = event.y()/self.scale
            if self.editRect():
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
            elif self.selend!=(None, None):
                if self.ui.core.verticalSplitter:
                    x = self.selend[0]
                    y = self.selend[1]
                    if self.ui.core.horizontalSplitter:
                        item.addChild(x1 = item.x1, y1 = item.y1, x2 = item.x1+x, y2 = item.y1+y)
                        item.addChild(x1 = item.x1+x, y1 = item.y1, x2 = item.x2, y2 = item.y1+y)
                        item.addChild(x1 = item.x1, y1 = item.y1+y, x2 = item.x1+x, y2 = item.y2)
                        item.addChild(x1 = item.x1+x, y1 = item.y1+y, x2 = item.x2, y2 = item.y2)
                    else:
                        item.addChild(x1 = item.x1, y1 = item.y1, x2 = item.x1+x, y2 = item.y2)
                        item.addChild(x1 = item.x1+x, y1 = item.y1, x2 = item.x2, y2 = item.y2)
                if self.ui.core.horizontalSplitter:
                    x = self.selend[0]
                    y = self.selend[1]
                    if self.ui.core.verticalSplitter:
                        item.addChild(x1 = item.x1, y1 = item.y1, x2 = item.x1+x, y2 = item.y1+y)
                        item.addChild(x1 = item.x1, y1 = item.y1+y, x2 = item.x1+x, y2 = item.y2)
                        item.addChild(x1 = item.x1+x, y1 = item.y1, x2 = item.x2, y2 = item.y1+y)
                        item.addChild(x1 = item.x1+x, y1 = item.y1+y, x2 = item.x2, y2 = item.y2)
                    else:
                        item.addChild(x1 = item.x1, y1 = item.y1, x2 = item.x2, y2 = item.y1+y)
                        item.addChild(x1 = item.x1, y1 = item.y1+y, x2 = item.x2, y2 = item.y2)
                if item.getType()=="Table":
                    if self.ui.core.tableRowSplitter:
                        y = self.selend[1]
                        item.addRowSep(y)
                    if self.ui.core.tableColumnSplitter:
                        x = self.selend[0]
                        item.addColSep(x)

            self.selstart = (None, None)
            self.selend = (None, None)
            self.mode = None
            self.update()

        def wheelEvent(self, event):
            self.scale += event.angleDelta().y()*self.scale/2048
            self.scale = min(self.scale, 10)
            self.scale = max(self.scale, 0.005)
            self.updateGeometry()

        def updateGeometry(self):
            self.resize(self.w*self.scale, self.h*self.scale)
            self.update()

        def editRect(self):
            editRect = True
            if self.ui.core.horizontalSplitter and self.selend!=(None, None):
                editRect = False
            if self.ui.core.verticalSplitter and self.selend!=(None, None):
                editRect = False
            if self.ui.core.tableRowSplitter and self.selend!=(None, None):
                editRect = False
            if self.ui.core.tableColumnSplitter and self.selend!=(None, None):
                editRect = False
            return editRect

        def paintEvent(self, event):
            if not self.item:
                return
            item = self.item
            item_painter = QtGui.QPainter(self)
            item.drawQT(item_painter, 0, 0, self.scale)

            fontSize = 6*item.scaleFactor
            padding = 1*item.scaleFactor

            painter = QtGui.QPainter(self)
            painter.setFont(QtGui.QFont('Consolas', fontSize))
            painter.scale(self.scale, self.scale)
            pen = QtGui.QPen(QtCore.Qt.red, 1/self.scale, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap)

            editRect = self.editRect()

            if editRect and self.selstart!=(None, None) and self.selend!=(None, None):
                sx0, sy0 = self.selstart
                sx1, sy1 = self.selend
                xoff = sx1 - sx0
                yoff = sy1 - sy0

                if len(self.ui.core.selections)==0: # new rect
                    pen.setColor(QtCore.Qt.blue)
                    painter.setPen(pen)
                    painter.drawRect(sx0,sy0,xoff,yoff)
            else:
                xoff = 0
                yoff = 0

            for i, child in enumerate(item.children):
                index = str(i+1)
                x1 = (child.x1-item.x1)
                y1 = (child.y1-item.y1)
                x2 = (child.x2-item.x1)
                y2 = (child.y2-item.y1)
                _x, _y = x1, y1
                _w, _h = x2-x1, y2-y1
                if i in self.ui.core.selections:
                    pen.setColor(QtCore.Qt.blue)
                    painter.setPen(pen)
                    if self.mode=='move':
                        _x = x1 + xoff
                        _y = y1 + yoff
                        painter.drawRect(_x, _y, x2-x1, y2-y1)
                    elif self.mode=='resize':
                        ex1, ex2 = asc(x1, x2+xoff)
                        ey1, ey2 = asc(y1, y2+yoff)
                        _x = ex1
                        _y = ey1
                        _w = ex2-ex1
                        _h = ey2-ey1
                        painter.drawRect(_x, _y, _w, _h)
                    else:
                        painter.drawRect(x1, y1, x2-x1, y2-y1)
                else:
                    pen.setColor(QtCore.Qt.red)
                    painter.setPen(pen)
                    painter.drawRect(x1, y1, x2-x1, y2-y1)
                _x += padding
                _y += padding
                _w -= 2*padding
                _h -= 2*padding
                painter.drawText(_x, _y, _w, _h, QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop, index)
                painter.drawText(_x, _y, _w, _h, QtCore.Qt.AlignRight|QtCore.Qt.AlignBottom, index)

            if item.getType()=="Table":
                pen.setColor(QtGui.QColor(0xff, 0xa5, 0x00))
                painter.setPen(pen)
                for x in item.colSep:
                    painter.drawLine(x, 0.0, x, item.y2-item.y1)
                for y in item.rowSep:
                    painter.drawLine(0.0, y, item.x2-item.x1, y)

            pen.setColor(QtCore.Qt.magenta)
            painter.setPen(pen)
            if self.ui.core.verticalSplitter and self.selend!=(None, None):
                painter.drawLine(self.selend[0], 0.0, self.selend[0], item.y2-item.y1)

            if self.ui.core.horizontalSplitter and self.selend!=(None, None):
                painter.drawLine(0.0, self.selend[1], item.x2-item.x1, self.selend[1])

            pen.setColor(QtCore.Qt.green)
            painter.setPen(pen)
            if self.ui.core.tableRowSplitter and self.selend!=(None, None):
                painter.drawLine(0.0, self.selend[1], item.x2-item.x1, self.selend[1])

            if self.ui.core.tableColumnSplitter and self.selend!=(None, None):
                painter.drawLine(self.selend[0], 0.0, self.selend[0], item.y2-item.y1)

        def resizeEvent(self, event):
            pass

        def zoomActual(self):
            self.scale = 1
            self.updateGeometry()

        def zoomFit(self):
            if self.w is None:
                return
            xscale = self.scrollArea.viewport().width() / self.w
            yscale = self.scrollArea.viewport().height() / self.h
            self.scale = min(xscale, yscale)
            self.updateGeometry()

        def onItemChanged(self):
            zoomFit = False
            if not self.item:
                zoomFit = True
            self.item = self.ui.core.getCurrentItem()
            if not self.item:
                return
            self.w, self.h = self.item.getSize()
            if zoomFit:
                self.zoomFit()
            else:
                self.updateGeometry()

        def reset(self):
            self.resize(0, 0)
            self.update()

    def __init__(self, ui, workAreaScroller):
        self.ui = ui
        self.workAreaScroller = workAreaScroller
        self.workArea = self.QWorkArea(self.workAreaScroller)
        self.workArea.ui = ui
        self.workAreaScroller.setWidget(self.workArea)

    def zoomActual(self):
        self.workArea.zoomActual()

    def zoomFit(self):
        self.workArea.zoomFit()

    def reset(self):
        self.workArea.reset()

    def onProjectChanged(self):
        self.reset()

    def onItemChanged(self):
        self.workArea.onItemChanged()

    def onSelectionChanged(self):
        self.workArea.update()

    def onContentChanged(self):
        self.workArea.update()
