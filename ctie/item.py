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

import os
import Image
import weakref
import math
import md5
import subprocess
from gi.repository import Gtk

import ctie
import imglib
from helpers import *
from cql import *

cache_gtk = {}
cache_pixbuf = {}
cache_pil_rgb = {}
cache_pil_l = {}

class Item(object):
	def __init__(self, path = None, parent = None, x1 = 0, y1 = 0, x2 = 0, y2 = 0, tags = {}):
		self.path = path
		self.parent = parent
		self.x1 = int(x1)
		self.y1 = int(y1)
		self.x2 = int(x2)
		self.y2 = int(y2)
		self.children = []
		self.tags = dict(tags)
		if self.path is None:
			self.path = parent.path

		self.hash = md5.new(self.path).hexdigest()

	def __str__(self):
		return "{0:X} # {1} ({2},{3},{4},{5})".format(id(self), os.path.basename(self.path), self.x1, self.y1, self.x2, self.y2)

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

	def get_thumbnail(self):
		tfile = os.path.join(get_tempdir(), "%s-%dx%dx%dx%d-thumbnail.jpg" % (self.hash, self.x1, self.y1, self.x2, self.y2))
		if not os.path.exists(tfile):
			im = Image.open(self.get_cropped())
			ow,oh = im.size
			nw,nh = (160,240)
			if float(ow)/oh>float(nw)/nh:
				newsize = (nw, int(math.ceil(float(nw)*oh/ow)))
			else:
				newsize = (int(math.ceil(float(nh)*ow/oh)), nh)
			if newsize[0]<im.size[0] and newsize[1]<im.size[1]:
				im.thumbnail(newsize)
			else:
				im = im.resize(newsize)
			im.save(tfile)
			del(im)
		return tfile

	def get_ocr_tempdir(self):
		rpath = "%s-%dx%dx%dx%d" % (self.hash, self.x1, self.y1, self.x2, self.y2)
		os.chdir(get_tempdir())
		return rpath

	def getTags(self):
		tags = {}
		t = self
		while t:
			for key in t.tags:
				if key not in tags:
					tags[key] = t.tags[key]
			t = t.parent
		return tags

	def setTag(self, key, value, isFormula = False):
		if isFormula:
			self.tags[key] = str(CQL(value).eval(self))
		else:
			self.tags[key] = value

	def unsetTag(self, key):
		del(self.tags[key])
		ctie.ui.onTagChanged()

	def contains(self, x, y):
		return x>self.x1 and x<self.x2 and y>self.y1 and y<self.y2

	def addChild(self, **arg):
		self.children.append(Item(parent = self, **arg))
		ctie.instance.ui.onItemTreeChanged()

	def removeChild(self, child):
		self.children.remove(child)
		ctie.instance.ui.onItemTreeChanged()

	def remove(self):
		ctie.instance.removeItem(self)
		if self.parent:
			self.parent.children.remove(self)
			ctie.instance.ui.onItemTreeChanged()

	def move(self, index, xoff, yoff):
		xoff = int(xoff)
		yoff = int(yoff)
		todo = [self.children[index]]
		while todo:
			delete = []
			newtodo = []
			for c in todo:
				x1 = c.x1+xoff
				y1 = c.y1+yoff
				x = c.x2+xoff
				y = c.y2+yoff
				x1 = max(x1, c.parent.x1)
				y1 = max(y1, c.parent.y1)
				x = min(x, c.parent.x2)
				y = min(y, c.parent.y2)
				c.x1 = min(x1, c.parent.x2)
				c.y1 = min(y1, c.parent.y2)
				c.x2 = max(x, c.parent.x1)
				c.y2 = max(y, c.parent.y1)
				if abs(x-x1)<=1 or abs(y-y1)<=1:
					delete.append(c)
				else:
					newtodo.extend(c.children)
			todo = newtodo
			for item in delete:
				item.remove()

	def resize(self, index, xoff, yoff):
		xoff = int(xoff)
		yoff = int(yoff)
		child = self.children[index]
		xoff2 = max(xoff, child.x1-child.x2)
		yoff2 = max(yoff, child.y1-child.y2)
		x1 = child.x1
		y1 = child.y1
		x = child.x2+xoff2
		y = child.y2+yoff2
		child.x1 = max(x1, self.x1)
		child.y1 = max(y1, self.y1)
		child.x2 = min(x, self.x2)
		child.y2 = min(y, self.y2)
		if abs(x-x1)<=1 or abs(y-y1)<=1:
			child.remove()

	def reorder_children(self, ordered_list = []):
		self.children = self.reordered_children(ordered_list)

	def reordered_children(self, ordered_list = []):
		r = []
		for i in ordered_list:
			r.append(self.children[i])
		for i,c in enumerate(self.children):
			if i not in ordered_list:
				r.append(c)
		return r

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
