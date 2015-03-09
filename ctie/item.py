"""
 Copyright (c) 2012-2014 Kuan-Chung Chiu <buganini@gmail.com>

 Permission to use, copy, modify, and distribute this software for any
 purpose with or without fee is hereby granted, provided that the above
 copyright notice and this permission notice appear in all copies.

 THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 WHATSOEVER RESULTING FROM LOSS OF MIND, USE, DATA OR PROFITS, WHETHER
 IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING
 OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""

import os
import Image
import weakref
import math
from gi.repository import Gtk

from helpers import *

id_map={}
cache_gtk={}
cache_pixbuf={}
cache_pil_rgb={}
cache_pil_l={}

class Item(object):
	def __init__(self, p):
		self.p=p
		self.hash=id_map[p['path']]

	def get_gtk(self):
		global cache_gtk
		oid=id(self.p)
		try:
			o=cache_gtk[oid]()
#			o=cache_gtk[oid]
		except:
			o=None
		if not o:
			o=Gtk.Image.new_from_file(self.get_cropped())
			cache_gtk[oid]=weakref.ref(o)
#			cache_gtk[oid]=o
		return o

	def get_pixbuf(self):
		global cache_pixbuf
		oid=id(self.p)
		try:
			o=cache_pixbuf[oid]()
		except:
			o=None
		if not o:
			o=self.get_gtk().get_pixbuf()
			cache_pixbuf[oid]=weakref.ref(o)
		return o

	def get_pil_rgb(self):
		global cache_pil_rgb
		oid=id(self.p['path'])
		try:
			o=cache_pil_rgb[oid]()
		except:
			o=None
		if not o:
			o=Image.open(self.p['path']).convert('RGB')
			cache_pil_rgb[oid]=weakref.ref(o)
		return o

	def get_pil_l(self):
		global cache_pil_l
		oid=id(self.p['path'])
		try:
			o=cache_pil_l[oid]()
		except:
			o=None
		if not o:
			o=Image.open(self.p['path']).convert('L')
			cache_pil_l[oid]=weakref.ref(o)
		return o

	def get_pil_cropped(self):
		return Image.open(self.p['path']).convert('RGB').crop((self.p['x1'], self.p['y1'], self.p['x2'], self.p['y2']))

	def get_cropped(self):
		bfile=os.path.join(get_tempdir(), "%s-%dx%dx%dx%d.jpg" % (self.hash, self.p['x1'], self.p['y1'], self.p['x2'], self.p['y2']))
		if not os.path.exists(bfile):
			im=self.get_pil_rgb().crop((self.p['x1'], self.p['y1'], self.p['x2'], self.p['y2']))
			im.save(bfile)
			del(im)
		return bfile

	def get_thumbnail(self):
		tfile=os.path.join(get_tempdir(), "%s-%dx%dx%dx%d-thumbnail.jpg" % (self.hash, self.p['x1'], self.p['y1'], self.p['x2'], self.p['y2']))
		if not os.path.exists(tfile):
			im=Image.open(self.get_cropped())
			ow,oh=im.size
			nw,nh=(160,240)
			if float(ow)/oh>float(nw)/nh:
				newsize=(nw, int(math.ceil(float(nw)*oh/ow)))
			else:
				newsize=(int(math.ceil(float(nh)*ow/oh)), nh)
			if newsize[0]<im.size[0] and newsize[1]<im.size[1]:
				im.thumbnail(newsize)
			else:
				im=im.resize(newsize)
			im.save(tfile)
			del(im)
		return tfile

	def get_ocr_tempdir(self):
		rpath="%s-%dx%dx%dx%d" % (self.hash, self.p['x1'], self.p['y1'], self.p['x2'], self.p['y2'])
		os.chdir(get_tempdir())
		return rpath

	def getTags(self):
		t=self.p
		tags={}
		while t:
			for tag in t['tags']:
				if tag not in tags:
					tags[tag]=t['tags'][tag]
			t=t['parent']
		return

	def reordered_children(self, ordered_list):
		r=[]
		for i in ordered_list:
			r.append(self.p['children'][i])
		for i,c in enumerate(self.p['children']):
			if i not in ordered_list:
				r.append(c)
		self.p['children'] = r
