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
import pypdfium2 as pdfium
import pdf
import os
import traceback

import cluto
import pillib
from item import Item as BaseItem

lastRender = None

class DummyImage:
	extension = "null"

	def save(self, path):
		return False

class Bundle():
    def __init__(self, items):
        self.items = items

    def save(self, path):
        for i, it in enumerate(self.items):
            it.save("{}.{}".format(path, i+1))

def is_image_page(page):
    """
    Check if a PDF page is essentially just an image.
    A page is considered an "image page" if it has image objects
    but no meaningful text content.
    """
    # Check for text content
    textpage = page.get_textpage()
    text = textpage.get_text_range().strip()
    textpage.close()

    # Check for image objects
    has_images = False
    for obj in page.get_objects():
        if obj.type == pdfium.raw.FPDF_PAGEOBJ_IMAGE:
            has_images = True
            break

    # Image page = has image(s) but no meaningful text
    return has_images and len(text) == 0

def rects_overlap(rect1, rect2):
    """Check if two rectangles overlap. Rects are (left, bottom, right, top)."""
    l1, b1, r1, t1 = rect1
    l2, b2, r2, t2 = rect2
    return not (r1 <= l2 or r2 <= l1 or t1 <= b2 or t2 <= b1)

def rect_intersection_area(rect1, rect2):
    """Calculate the intersection area of two rectangles."""
    l1, b1, r1, t1 = rect1
    l2, b2, r2, t2 = rect2

    inter_left = max(l1, l2)
    inter_bottom = max(b1, b2)
    inter_right = min(r1, r2)
    inter_top = min(t1, t2)

    if inter_right <= inter_left or inter_top <= inter_bottom:
        return 0.0
    return (inter_right - inter_left) * (inter_top - inter_bottom)

def find_images_in_rect(page, target_rect, min_overlap=0.8):
    """
    Find image objects that overlap with a target rectangle.

    Args:
        page: pypdfium2 page object
        target_rect: (left, bottom, right, top) in PDF coordinates
        min_overlap: minimum fraction of the image that must be inside the rect

    Returns:
        List of matching image objects with their positions
    """
    images = []

    for obj in page.get_objects():
        if obj.type != pdfium.FPDF_PAGEOBJ_IMAGE:
            continue

        img_rect = obj.get_pos()  # (left, bottom, right, top)

        if not rects_overlap(img_rect, target_rect):
            continue

        # Calculate how much of the image is inside the target rect
        l, b, r, t = img_rect
        img_area = abs(r - l) * abs(t - b)
        if img_area == 0:
            continue

        overlap_area = rect_intersection_area(img_rect, target_rect)
        overlap_ratio = overlap_area / img_area

        if overlap_ratio >= min_overlap:
            images.append(obj.get_bitmap().to_pil())

    return images

class PdfItem(BaseItem):
    @staticmethod
    def probe(filename):
        return filename.lower().endswith(".pdf")

    @staticmethod
    def addItem(core, path):
        pdf = pdfium.PdfDocument(os.path.join(core.workspace, path))
        pages = len(pdf)
        for i in range(pages):
            item = PdfItem(doc = pdf, page = i, path = path, x1 = 0, y1 = 0, x2 = -1, y2 = -1)
            core.clips.append(item)

    unit = 96 / 72
    def __init__(self, doc=None, page=None, **args):
        super(PdfItem, self).__init__(**args)
        self.page = page
        if self.page is None:
            self.page = self.parent.page
        if self.x2==-1 or self.y2==-1:
            page = self.getPdfPage()
            self.x2 = page.get_width() * self.unit
            self.y2 = page.get_height() * self.unit
            page.close()

    def getTitle(self):
        return "{} p{}".format(os.path.basename(self.path), self.page+1)

    def getTypes(self):
        return ("Text", "Image", "Images", "ObjectImage", "Table")

    def getDefaultType(self):
        return "Text"

    def getImage(self, scale=4):
        page = self.getPdfPage()
        if is_image_page(page):
            w = page.get_width() * self.unit
            h = page.get_height() * self.unit
            pil_image = page.render(
                scale=scale * self.unit,
                rotation=0,
                crop=(self.x1/self.unit, (h - self.y2)/self.unit, (w - self.x2)/self.unit, self.y1/self.unit)
            ).to_pil().convert("RGB")
            page.close()
            return pil_image
        else:
            images = find_images_in_rect(page, (self.x1, self.y1, self.x2, self.y2))
            if len(images) == 0:
                return DummyImage()
            else:
                return images[0]

    def getImages(self, scale=4):
        page = self.getPdfPage()
        if is_image_page(page):
            w = page.get_width() * self.unit
            h = page.get_height() * self.unit
            pil_image = page.render(
                scale=scale * self.unit,
                rotation=0,
                crop=(self.x1/self.unit, (h - self.y2)/self.unit, (w - self.x2)/self.unit, self.y1/self.unit)
            ).to_pil().convert("RGB")
            page.close()
            return pil_image
        else:
            images = find_images_in_rect(page, (self.x1, self.y1, self.x2, self.y2))
            if len(images) == 0:
                return DummyImage()
            elif len(images) == 1:
                return images[0]
            else:
                return Bundle(images)

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
        try:
            page = self.getPdfPage()
            w = page.get_width() * self.unit
            h = page.get_height() * self.unit
            pil_image = page.render(
                scale=scale * self.unit,
                rotation=0,
                crop=(self.x1/self.unit, (h - self.y2)/self.unit, (w - self.x2)/self.unit, self.y1/self.unit)
            ).to_pil().convert("RGBA")
            page.close()
            qimage = QtGui.QImage(
                pil_image.tobytes(),
                pil_image.width,
                pil_image.height,
                QtGui.QImage.Format.Format_RGBA8888
            )
            painter.drawImage(xoff, yoff, qimage)
        except:
            traceback.print_exc()
            return None

    def getPdfPage(self):
        return pdfium.PdfDocument(self.getFullPath())[self.page]

    def _getLines(self):
        return pdf.getLines(self.getFullPath(), self.page, self.x1, self.y1, self.x2, self.y2)

    def get_pil_l(self):
        page = self.getPdfPage()
        w = page.get_width() * self.unit
        h = page.get_height() * self.unit
        o = page.render(
            scale=1 * self.unit,
            rotation=0,
            crop=(0, 0, 0, 0)
        ).to_pil().convert("L")
        page.close()
        return o

    def trim(self, left, top, right, bottom, margin=0):
        x1 = self.x1
        y1 = self.y1
        x2 = self.x2
        y2 = self.y2

        if self.getType() == "ObjectImage":
            im = self.getImage(scale=1)
            from rembg import remove, new_session
            im = remove(im)
            im = im.convert("L")
            w, h = im.size

            if left:
                nx1 = pillib.leftTrim(im, 0, 0, w, h, margin)
            if top:
                ny1 = pillib.topTrim(im, 0, 0, w, h, margin)
            if right:
                nx2 = pillib.rightTrim(im, 0, 0, w, h, margin)
            if bottom:
                ny2 = pillib.bottomTrim(im, 0, 0, w, h, margin)

            x1 += nx1
            y1 += ny1
            x2 -= w - nx2
            y2 -= h - ny2

        else:
            im = self.get_pil_l()

            if left:
                x1 = pillib.leftTrim(im, x1, y1, x2, y2, margin)
            if top:
                y1 = pillib.topTrim(im, x1, y1, x2, y2, margin)
            if right:
                x2 = pillib.rightTrim(im, x1, y1, x2, y2, margin)
            if bottom:
                y2 = pillib.bottomTrim(im, x1, y1, x2, y2, margin)

        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        cluto.instance.worker.addBgJob(self)

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

        text = self.paddle_ocr(tmpfile)

        self.tags['ocr_raw'] = text
        text = cluto.instance.evalRegex(text)
        self.tags['text'] = text
        cluto.instance.addTag('ocr_raw')
        cluto.instance.addTag('text')