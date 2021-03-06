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

import cluto
from item import Item as BaseItem

cache_pdf = {}
cache_pdf_page = {}
lastRender = None

class PdfItem(BaseItem):
    @staticmethod
    def probe(filename):
        return filename.lower().endswith(".pdf")

    @staticmethod
    def addItem(core, path):
        pdf = QtPoppler.Document.load(os.path.join(core.workspace, path))
        for i in range(pdf.numPages()):
            item = PdfItem(doc = pdf, page = i, path = path, x1 = 0, y1 = 0, x2 = -1, y2 = -1)
            core.clips.append(item)

    scaleFactor = 100
    def __init__(self, doc=None, page=None, **args):
        global cache_pdf
        super(PdfItem, self).__init__(**args)
        self.page = page
        if self.page is None:
            self.page = self.parent.page
        if doc:
            cache_pdf[self.path] = doc
        if self.x2==-1 or self.y2==-1:
            self.x2, self.y2 = pdf.getPageSize(self.getFullPath(), self.page)

    def getTitle(self):
        return "{} p{}".format(os.path.basename(self.path), self.page+1)

    def getTypes(self):
        return ("Text", "Image", "Images", "Table")

    def getDefaultType(self):
        return "Text"

    def getImage(self):
        image = self.cache.get("image")
        if image is None:
            image = pdf.getImage(self.getFullPath(), self.page, self.x1, self.y1, self.x2, self.y2)
            self.cache["image"] = image
        return image

    def getImages(self):
        images = self.cache.get("images")
        if images is None:
            images = pdf.getImage(self.getFullPath(), self.page, self.x1, self.y1, self.x2, self.y2, multiple=True)
            self.cache["images"] = images
        return images

    def getText(self):
        text = self.cache.get("text")
        if text is None:
            text = pdf.getText(self.getFullPath(), self.page, self.x1, self.y1, self.x2, self.y2)
            self.cache["text"] = text
        return text

    def getTable(self):
        table = self.cache.get("table")
        if table is None:
            table = pdf.getTable(self.getFullPath(), self.page, self.x1, self.y1, self.x2, self.y2, rSep=self.rowSep, cSep=self.colSep)
            self.cache["table"] = table
        return table

    def getContent(self):
        if self.getType()=="Text":
            return self.getText()
        elif self.getType()=="Image":
            return self.getImage()
        elif self.getType()=="Images":
            return self.getImages()
        elif self.getType()=="Table":
            return self.getTable()
        else:
            return None

    def drawQT(self, painter, xoff, yoff, scale=1):
        image = self.getPdfImage(scale)
        painter.drawImage(xoff, yoff, image)

    def getPdfImage(self, scale):
        return self.getPdfPage().renderToImage(7200*scale, 7200*scale, self.x1*scale, self.y1*scale, (self.x2-self.x1)*scale, (self.y2-self.y1)*scale)

    def getPdfPage(self):
        global cache_pdf, cache_pdf_page
        if self.path not in cache_pdf:
            doc = QtPoppler.Document.load(self.getFullPath())
            doc.setRenderHint(QtPoppler.Document.Antialiasing)
            doc.setRenderHint(QtPoppler.Document.TextAntialiasing)
            cache_pdf[self.path] = doc
        if self.path not in cache_pdf_page:
            cache_pdf_page[self.path]={}
        if self.page not in cache_pdf_page[self.path]:
            cache_pdf_page[self.path][self.page] = cache_pdf[self.path].page(self.page)
        return cache_pdf_page[self.path][self.page]

    def _getLines(self):
        return pdf.getLines(self.getFullPath(), self.page, self.x1, self.y1, self.x2, self.y2)

    def ocr(self):
        if 'text' in self.tags:
            return
        tempdir = os.path.join(self.getWorkdir(), "ocr")
        if not os.path.exists(tempdir):
            os.makedirs(tempdir)
        im = self.getPdfImage(1)
        tmpfile = os.path.join(tempdir, "clip.bmp")
        im.save(tmpfile)
        del(im)
        os.chdir(tempdir)

        text = self.tesseract_ocr(tmpfile)

        self.tags['ocr_raw'] = text
        text = cluto.instance.evalRegex(text)
        self.tags['text'] = text
        cluto.instance.addTag('ocr_raw')
        cluto.instance.addTag('text')