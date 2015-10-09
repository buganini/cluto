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
import pickle

from gi.repository import Poppler

from imageItem import *
from pdfItem import *
from cql import *
from helpers import *

instance = None

class Ctie(object):
	def __init__(self, ui, path = None):
		global instance
		instance = self
		self.ui = ui
		self.regex = []
		self.clips = []
		self.tags = []
		self.filter = None
		self.items = []
		self.currentLevel = -1
		self.currentIndex = None
		self.selections = []
		self.clipboard = []
		self.copy_tags = []
		self.tempdir = get_tempdir()
		self.bulkMode = True

	def getLevel(self):
		l = 0
		s = self.clips
		while s:
			l+=1
			ns = []
			for x in s:
				ns.extend(x.children)
			s = ns
		return l

	def setLevel(self, level):
		r = False
		orig = self.getCurrentItem()
		if self.currentLevel != level:
			r = True
			self.currentLevel = level
			self._genItems()
			self.currentIndex = 0
			self.ui.onItemListChanged()
		item = self.getCurrentItem()
		if orig != item:
			self.ui.onItemBlurred(orig)
			self.ui.onItemFocused()
		return r

	def selectAllChildren(self):
		item = self.getCurrentItem()
		if item is None:
			return
		self.selections = range(0, len(item.children))
		self.ui.onSelectionChanged()

	def deselectAllChildren(self):
		self.selections = []
		self.ui.onSelectionChanged()

	def selectChildByIndex(self, index):
		item = self.getCurrentItem()
		if item is None:
			return
		if index not in self.selections and index < len(item.children):
			self.selections.append(index)
		self.ui.onSelectionChanged()

	def deselectChildByIndex(self, index):
		if index in self.selections:
			self.selections.remove(index)
		self.ui.onSelectionChanged()

	def selectItemByIndex(self, index):
		orig = self.getCurrentItem()
		self.currentIndex = index
		item = self.getCurrentItem()
		if orig != item:
			self.selections = []
			self.ui.onItemBlurred(orig)
			self.ui.onItemFocused()
		self.selections = []
		self.ui.onItemChanged()

	def selectNextItem(self):
		orig = self.getCurrentItem()
		self.currentIndex = (self.currentIndex + 1) % len(self.items)
		item = self.getCurrentItem()
		if orig != item:
			self.selections = []
			self.ui.onItemBlurred(orig)
			self.ui.onItemFocused()
		self.ui.onItemChanged()

	def selectPrevItem(self):
		orig = self.getCurrentItem()
		self.currentIndex = (self.currentIndex + len(self.items) - 1) % len(self.items)
		item = self.getCurrentItem()
		if orig != item:
			self.selections = []
			self.ui.onItemBlurred(orig)
			self.ui.onItemFocused()
		self.ui.onItemChanged()

	def getCurrentItem(self):
		if self.currentIndex is None:
			return None
		l = self.items[self.currentIndex:]
		if l:
			return l[0]
		return None

	def _genItems(self):
		if self.bulkMode:
			return
		self.selections = []
		s = self.clips
		for i in range(0, self.currentLevel):
			ns = []
			for x in s:
				ns.extend(x.children)
			s = ns
		items = []
		for p in s:
			if self.filter and not self.filter.eval(p):
				continue
			items.append(p)
		for item in self.items:
			if item not in items and hasattr(self, "ui"):
				self.ui.onItemRemoved(item)
		self.items = items

	def addItemByPath(self, path):
		if os.path.isdir(path):
			cs = os.listdir(path)
			cs.sort(natcmp)
			for c in cs:
				self.addItemByPath(os.path.join(path,c))
		else:
			if PdfItem.probe(path):
				pdf = Poppler.Document.new_from_file("file://"+path, None)
				for i in range(pdf.get_n_pages()):
					item = PdfItem(pdf = pdf, page = i, path = path, x1 = 0, y1 = 0, x2 = -1, y2 = -1)
					self.clips.append(item)
			elif ImageItem.probe(path):
				item = ImageItem(path = path, x1 = 0, y1 = 0, x2 = -1, y2 = -1)
				self.clips.append(item)
		self._genItems()
		self.ui.onItemListChanged()
		if len(self.clips)==1:
			self.selectItemByIndex(0)

	def removeItem(self, item):
		focusedItem = self.getCurrentItem()
		if item.parent == focusedItem:
			index = focusedItem.children.index(item)
			if index in self.selections:
				self.selections.remove(index)
		if item in self.clips:
			self.clips.remove(item)
		if item in self.items:
			self.items.remove(item)
		self.ui.onItemTreeChanged()

	def getRegex(self):
		l = []
		for r in self.regex:
			l.append("\t".join(r))
		return "\n".join(l)

	def setRegex(self, text):
		self.regex = []
		for line in text.split("\n"):
			try:
				a,b = line.split("\t")
				self.regex.append((a, b))
			except:
				pass

	def evalRegex(self, text):
		for pattern, replacement in self.regex:
			text2 = re.sub(pattern, replacement, text)
			text = text2
		return text

	def setFilter(self, filter):
		f = CQL(filter)
		r = False
		if f or filter=="":
			self.filter = f
			r = True
			self._genItems()
			self.ui.onItemListChanged()
		return r

	def load(self, path):
		fp = open(path,'r')
		try:
			data = pickle.load(fp)
			fp.close()
		except:
			return False
		self.clips = data['clips']
		self.tags = data['tags']
		self.copy_tags = data['tags']
		self.tempdir = data['tempdir']
		if not os.path.exists(self.tempdir):
			os.makedirs(self.tempdir)
		self.regex = data['regex']
		self.ui.onItemTreeChanged()
		self.ui.onItemChanged()
		return True

	def save(self, path):
		for item in self.items:
			self.ui.onItemRemoved(item)
		data = {'clips':self.clips, 'tags':self.tags, 'copy_tags':self.copy_tags, 'tempdir':self.tempdir, 'regex':self.regex}
		fp = open(path,'w')
		pickle.dump(data, fp)
		fp.close()

	def export(self, export_filter, export_content, export_path, outputdir):
		todo = self.clips
		while todo:
			newtodo = []
			for item in todo:
				if export_filter.eval(item):
					t = item
					tags = {}
					while t:
						for key in t.tags:
							if key not in tags:
								tags[key] = t.tags[key]
						t = t.parent
					for key in self.tags:
						if key not in tags:
							tags[key] = ""

					path = export_path.eval(item)
					path = os.path.join(outputdir, path)
					pdir = os.path.dirname(path)
					if not os.path.exists(pdir):
						os.makedirs(pdir)
					if os.path.exists(path):
						print "Exists:", path
					cnt = export_content.eval(item)
					if hasattr(cnt, "save"):
						cnt.save(path)
					else:
						f = open(path,'w')
						f.write(cnt)
						f.close()
				newtodo.extend(item.children)
			todo = newtodo

	def copy(self):
		item = self.getCurrentItem()
		if item is None:
			return
		self.clipboard = []
		for i in self.selections:
			child = item.children[i]
			tags = {}
			for key in self.copy_tags:
				if key in child.tags:
					tags[key] = child.tags[key]
			self.clipboard.append({'x1':child.x1-item.x1, 'y1':child.y1-item.y1, 'x2':child.x2-item.x1 ,'y2':child.y2-item.y1 ,'tags':tags})

	def paste(self):
		if not self.clipboard:
			return
		item = self.getCurrentItem()
		if item is None:
			return
		self.selections = []
		cs = []
		for child in item.children:
			cs.append((child.x1-item.x1, child.y1-item.y1, child.x2-item.x1, child.y2-item.y1))
		for p in self.clipboard:
			x1 = p['x1']
			y1 = p['y1']
			x2 = p['x2']
			y2 = p['y2']
			x1 = max(x1, 0)
			y1 = max(y1, 0)
			x2 = min(x2, item.x2-item.x1)
			y2 = min(y2, item.y2-item.y1)
			if x2-x1>1 and y2-y1>1:
				self.selections.append(len(item.children))
				if (x1,y1,x2,y2) in cs:
					continue
				item.addChild(x1 = x1+item.x1, y1 = y1+item.y1, x2 = x2+item.x1, y2 = y2+item.y1, tags = p['tags'])

	def autoPaste(self):
		threshold = 30
		if not self.clipboard:
			return
		item = self.getCurrentItem()
		if item is None:
			return
		for item in self.items:
			if item.children:
				continue
			im = Image.open(item.path).convert('L')
			paste = True
			clipboard = []
			for p in self.clipboard:
				x1 = p['x1']
				y1 = p['y1']
				x2 = p['x2']
				y2 = p['y2']
				x1 = max(x1, 0)
				y1 = max(y1, 0)
				x2 = min(x2, item.x2-item.x1)
				y2 = min(y2, item.y2-item.y1)

				lastpixel = im.getpixel((x1+item.x1, y1+item.y1))
				if y1!=0:
					y = y1+item.y1
					for x in range(x1+item.x1+1, x2+item.x1-1):
						pixel = im.getpixel((x,y))
						if abs(pixel-lastpixel)>threshold:
							paste = False
							break
						lastpixel = pixel
					if not paste:
						break
				if x2!=item.x2-item.x1:
					x = x2+item.x1-1
					for y in range(y1+item.y1+1,y2+item.y1-1):
						pixel = im.getpixel((x,y))
						if abs(pixel-lastpixel)>threshold:
							paste = False
							break
						lastpixel = pixel
					if not paste:
						break
				if y2!=item.y2-item.y1:
					y = y2+item.y1-1
					for x in range(x1+item.x1+1,x2+item.x1):
						pixel = im.getpixel((x,y))
						if abs(pixel-lastpixel)>threshold:
							paste = False
							break
						lastpixel = pixel
					if not paste:
						break
				if x1!=0:
					x = x1+item.x1
					for y in range(y1+item.y1+1,y2+item.y1):
						pixel = im.getpixel((x,y))
						if abs(pixel-lastpixel)>threshold:
							paste = False
							break
						lastpixel = pixel
					if not paste:
						break
				clipboard.append({'x1':x1, 'y1':y1, 'x2':x2, 'y2':y2, 'tags':p['tags']})
			del(im)
			for p in clipboard:
				if x2-x1>1 and y2-y1>1:
					item.addChild(x1 = p['x1']+item.x1, y1 = p['y1']+item.y1, x2 = p['x2']+item.x1, y2 = p['y2']+item.y1, tags = p['tags'])

	def deleteSelectedChildren(self):
		item = self.getCurrentItem()
		if item is None:
			return
		self.selections.sort()
		self.selections.reverse()
		for i in self.selections:
			del(item.children[i])
		self.selections = []
		self.ui.onItemTreeChanged()

	def enableCopyTag(self, key):
		if key in self.tags and key not in self.copy_tags:
			self.copy_tags.append(key)

	def disableCopyTag(self, key):
		if key in self.copy_tags:
			self.copy_tags.remove(key)

	def addTag(self, key):
		if key.startswith("_"):
			return
		if not key in self.tags:
			self.tags.append(key)
		self.ui.onTagChanged()

	def getTags(self, item = None):
		if item is None:
			return self.tags
		tags = item.getTags()
		for tag in self.tags:
			if tag not in tags:
				tags[tag] = ""
		return tags

	def batchSetTag(self, key, value, isFormula):
		if key not in self.tags:
			self.tags.append(key)
		for it in self.items:
			it.setTag(key, value, isFormula)
		self.ui.onTagChanged()

	def selectPrevChild(self):
		item = self.getCurrentItem()
		if item is None:
			return
		if not item.children:
			pass
		elif len(self.selections)!=1:
			self.selections = [0]
		else:
			self.selections[0] += len(item.children)-1
			self.selections[0] %= len(item.children)
		self.ui.onSelectionChanged()


	def selectNextChild(self):
		item = self.getCurrentItem()
		if item is None:
			return
		if not item.children:
			pass
		elif len(self.selections)!=1:
			self.selections = [0]
		else:
			self.selections[0] += 1
			self.selections[0] %= len(item.children)
		self.ui.onSelectionChanged()

	def move(self, xoff, yoff):
		item = self.getCurrentItem()
		if item is None:
			return
		for i in self.selections:
			item.move(i, xoff, yoff)

	def resize(self, xoff, yoff):
		item = self.getCurrentItem()
		if item is None:
			return
		selections = list(self.selections)
		selections.sort(reverse = True)
		for i in selections:
			item.resize(i, xoff, yoff)


	def reorder_children(self):
		item = self.getCurrentItem()
		if item is None:
			return
		item.reorder_children(self.selections)
		self.selections = range(0,len(item.children))
		self.ui.onSelectionChanged()

	def leftTopTrim(self):
		for item in self.items:
			item.leftTopTrim()
		self.edge_limiter(self.items)

	def rightBottomTrim(self):
		for item in self.items:
			item.rightBottomTrim()
		self.edge_limiter(self.items)

	def edge_limiter(self, todo):
		while todo:
			delete = []
			newtodo = []
			for item in todo:
				x1 = item.x1
				y1 = item.y1
				x = item.x2
				y = item.y2
				if x1>x:
					x1,x = x,x1
				if y1>y:
					y1,y = y,y1
				if item.parent:
					item.x1 = max(x1, item.parent.x1)
					item.y1 = max(y1, item.parent.y1)
					item.x2 = min(x, item.parent.x2)
					item.y2 = min(y, item.parent.y2)
				if abs(x-x1)<=1 or abs(y-y1)<=1:
					delete.append(item)
				else:
					newtodo.extend(item.children)
			todo = newtodo
			for item in delete:
				if item.parent:
					item.parent.children.remove(item)
				else:
					self.clips.remove(item)
