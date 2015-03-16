"""
 Copyright (c) 2012-2015 Kuan-Chung Chiu <buganini@gmail.com>

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

from gi.repository import Gtk, Gdk
import os
import math
import Image
import subprocess
import weakref

from helpers import *
from item import Item
import imglib

cache_pixbuf = {}
cache_gtk = {}
cache_pil_rgb = {}
cache_pil_l = {}

class ImageItem(Item):
	def __init__(self, **args):
		super(ImageItem, self).__init__(**args)
		if self.x2==-1 or self.y2==-1:
			im = Image.open(self.path)
			self.x2, self.y2 = im.size
			del(im)

	def get_gtk(self):
		global cache_gtk
		oid = id(self)
		try:
			o = cache_gtk[oid]()
		except:
			o = None
		if not o:
			o = Gtk.Image.new_from_file(self.get_cropped())
			cache_gtk[oid] = weakref.ref(o)
		return o

	def get_pixbuf(self):
		global cache_pixbuf
		oid = id(self)
		try:
			o = cache_pixbuf[oid]()
		except:
			o = None
		if not o:
			o = self.get_gtk().get_pixbuf()
			cache_pixbuf[oid] = weakref.ref(o)
		return o

	def get_pil_rgb(self):
		global cache_pil_rgb
		oid = id(self.path)
		try:
			o = cache_pil_rgb[oid]()
		except:
			o = None
		if not o:
			o = Image.open(self.path).convert('RGB')
			cache_pil_rgb[oid] = weakref.ref(o)
		return o

	def get_pil_l(self):
		global cache_pil_l
		oid = id(self.path)
		try:
			o = cache_pil_l[oid]()
		except:
			o = None
		if not o:
			o = Image.open(self.path).convert('L')
			cache_pil_l[oid] = weakref.ref(o)
		return o

	def get_pil_cropped(self):
		return Image.open(self.path).convert('RGB').crop((self.x1, self.y1, self.x2, self.y2))

	def get_cropped(self):
		bfile = os.path.join(get_tempdir(), "%s-%dx%dx%dx%d.jpg" % (self.hash, self.x1, self.y1, self.x2, self.y2))
		if not os.path.exists(bfile):
			im = self.get_pil_rgb().crop((self.x1, self.y1, self.x2, self.y2))
			im.save(bfile)
			del(im)
		return bfile

	def get_ocr_tempdir(self):
		rpath = "%s-%dx%dx%dx%d" % (self.hash, self.x1, self.y1, self.x2, self.y2)
		os.chdir(get_tempdir())
		return rpath

	def drawThumbnail(self, widget, cr):
		tfile = os.path.join(get_tempdir(), "%s-%dx%dx%dx%d-thumbnail.jpg" % (self.hash, self.x1, self.y1, self.x2, self.y2))
		if not os.path.exists(tfile):
			im = Image.open(self.get_cropped())
			ow,oh = im.size
			nw,nh = (widget.get_allocated_width(), widget.get_allocated_height())
			if float(ow)/oh>float(nw)/nh:
				self.thumbnail_size = (nw, int(math.ceil(float(nw)*oh/ow)))
			else:
				self.thumbnail_size = (int(math.ceil(float(nh)*ow/oh)), nh)
			if self.thumbnail_size[0]<im.size[0] and self.thumbnail_size[1]<im.size[1]:
				im.thumbnail(self.thumbnail_size)
			else:
				im = im.resize(self.thumbnail_size)
			im.save(tfile)
			del(im)
		pb = Gtk.Image.new_from_file(tfile).get_pixbuf()
		Gdk.cairo_set_source_pixbuf(cr, pb, (widget.get_allocated_width()-self.thumbnail_size[0])/2, (widget.get_allocated_height()-self.thumbnail_size[1])/2)
		cr.paint()

	def draw(self, widget, cr):
		Gdk.cairo_set_source_pixbuf(cr, self.get_pixbuf(), 0, 0)
		cr.paint()

	def ocr(self):
		if 'text' in self.tags:
			return
		tempdir = self.get_ocr_tempdir()
		if not os.path.exists(tempdir):
			os.makedirs(tempdir)
		im = self.get_pil_cropped()
		im.save(os.path.join(tempdir, "clip.png"))
		del(im)
		os.chdir(tempdir)
		subprocess.call(["tesseract", "clip.png", "out"])
		text = open("out.txt").read().rstrip().decode("utf-8")
		text = ctie.instance.evalRegex(text)
		self.tags['text'] = text
		ctie.instance.addTag('text')

	def leftTopTrim(self):
		x1 = self.x1
		y1 = self.y1
		x2 = self.x2
		y2 = self.y2
		im = self.get_pil_l()

		self.x1 = imglib.leftTrim(im, x1, y1, x2, y2)
		self.y1 = imglib.topTrim(im, x1, y1, x2, y2)

	def rightBottomTrim(self):
		x1 = self.x1
		y1 = self.y1
		x2 = self.x2
		y2 = self.y2
		im = self.get_pil_l()

		self.x2 = imglib.rightTrim(im, x1, y1, x2, y2)
		self.y2 = imglib.bottomTrim(im, x1, y1, x2, y2)
