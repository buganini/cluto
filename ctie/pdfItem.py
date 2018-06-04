"""
 Copyright (c) 2015 Kuan-Chung Chiu <buganini@gmail.com>

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions
 are met:
 1. Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
 2. Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.

 THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
 ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
 FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 SUCH DAMAGE.
"""

from PyQt5 import QtGui
from popplerqt5 import Poppler as QtPoppler
import pdf
import os

import ctie
from item import Item as BaseItem

cache_pdf = {}
cache_pdf_page = {}
cache_pdf_page_image = {}
lastRender = None

class PdfItem(BaseItem):
    @staticmethod
    def probe(filename):
        return filename.lower().endswith(".pdf")

    @staticmethod
    def addItem(core, path):
        pdf = QtPoppler.Document.load(os.path.join(core.workspace, path))
        for i in range(pdf.numPages()):
            item = PdfItem(pdf = pdf, page = i, path = path, x1 = 0, y1 = 0, x2 = -1, y2 = -1)
            core.clips.append(item)

    def __init__(self, pdf=None, page=None, **args):
        global cache_pdf
        super(PdfItem, self).__init__(**args)
        self.page = page
        if self.page is None:
            self.page = self.parent.page
        if pdf:
            cache_pdf[self.path] = pdf
        if self.x2==-1 or self.y2==-1:
            size = self.getPdfPage().pageSizeF()
            self.x2 = size.width()
            self.y2 = size.height()
        self.text = None
        self.image = None
        self.table = None
        self.rowSep = []
        self.colSep = []


    def addRowSep(self, pos):
        self.rowSep.append(pos)
        self.rowSep.sort()

    def addColSep(self, pos):
        self.colSep.append(pos)
        self.colSep.sort()

    def getTypes(self):
        return ("Text", "Image", "Table")

    def getType(self):
        if self.parent:
            default = self.parent.getType()
        else:
            default = "Text"
        return self.tags.get("_type", default)

    def getExtension(self):
        if self.getType()=="Text":
            return "txt"
        elif self.getType()=="Image":
            if self.image is None:
                self.image = pdf.getImage(os.path.join(ctie.instance.workspace, self.path), self.page, self.x1*100, self.y1*100, self.x2*100, self.y2*100)
            return self.image.extension
        elif self.getType()=="Table":
            return "csv"
        else:
            return ""

    def getContent(self):
        if self.getType()=="Text":
            if self.text is None:
                self.text = pdf.getText(os.path.join(ctie.instance.workspace, self.path), self.page, self.x1*100, self.y1*100, self.x2*100, self.y2*100)
            return self.text
        elif self.getType()=="Image":
            if self.image is None:
                self.image = pdf.getImage(os.path.join(ctie.instance.workspace, self.path), self.page, self.x1*100, self.y1*100, self.x2*100, self.y2*100)
            return self.image
        elif self.getType()=="Table":
            # if self.table is None:
            self.table = pdf.getTable(os.path.join(ctie.instance.workspace, self.path), self.page, self.x1*100, self.y1*100, self.x2*100, self.y2*100, rSep=[x*100 for x in self.rowSep], cSep=[x*100 for x in self.colSep])
            return self.table
        else:
            return None

    def drawQT(self, painter, scale=1):
        image = self.getPdfPageImage(scale)
        painter.drawImage(0, 0, image, self.x1*scale, self.y1*scale, (self.x2-self.x1)*scale, (self.y2-self.y1)*scale)

    def getPdfPageImage(self, scale):
        global cache_pdf_page_image
        if self.hash not in cache_pdf_page_image:
            cache_pdf_page_image[self.hash]={}
        if scale not in cache_pdf_page_image[self.hash]:
            cache_pdf_page_image[self.hash][scale] = self.getPdfPage().renderToImage(72*scale, 72*scale)
        return cache_pdf_page_image[self.hash][scale]

    def getPdfPage(self):
        global cache_pdf, cache_pdf_page
        if self.path not in cache_pdf:
            doc = QtPoppler.Document.load(os.path.join(ctie.instance.workspace, self.path))
            doc.setRenderHint(QtPoppler.Document.Antialiasing)
            doc.setRenderHint(QtPoppler.Document.TextAntialiasing)
            cache_pdf[self.path] = doc
        if self.path not in cache_pdf_page:
            cache_pdf_page[self.path]={}
        if self.page not in cache_pdf_page[self.path]:
            cache_pdf_page[self.path][self.page] = cache_pdf[self.path].page(self.page)
        return cache_pdf_page[self.path][self.page]
