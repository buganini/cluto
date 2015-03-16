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

from gi.repository import Poppler

from item import Item

class PdfItem(Item):
	def __init__(self, pdf=None, page=None, **args):
		super(PdfItem, self).__init__(**args)
		self.pdf = pdf
		if self.pdf is None:
			self.pdf = self.parent.pdf
		self.page = page
		if self.page is None:
			self.page = self.parent.page
		self.pdfPage = self.pdf.get_page(self.page)
		# print dir(self.pdfPage)
		if self.x2==-1 or self.y2==-1:
			self.x2, self.y2 = self.pdfPage.get_size()

	def drawThumbnail(self, widget, cr):
		cr.set_source_rgba(255,255,255,255)
		cr.paint()
		self.pdfPage.render(cr)

	def draw(self, widget, cr):
		cr.set_source_rgba(255,255,255,255)
		cr.paint()
		self.pdfPage.render(cr)

