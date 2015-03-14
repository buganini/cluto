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
import md5

from item import *
from helpers import *

class Ctie(object):
	def __init__(self, ui, path=None):
		self.regex = []
		self.clips = []
		self.tags = []
		self.filter = None
		self.items = []
		self.currentLevel = -1
		self.currentIndex = -1
		self.selections=[]
		self.clipboard=[]
		self.copy_tags=[]

	def getLevel(self):
		l=0
		s=self.clips
		while s:
			l+=1
			ns=[]
			for x in s:
				ns.extend(x['children'])
			s=ns
		return l

	def setLevel(self, level):
		r = False
		if self.currentLevel != level:
			r = True
			self.currentLevel = level
			self._genItems()
		return r

	def getSelections(self):
		return self.selections

	def selectAllChildren(self):
		item = self.getCurrentItem()
		if item is None:
			return
		self.selections = range(0, len(item["children"]))

	def selectNoneChildren(self):
		self.selections = []

	def setCurrentIndex(self, index):
		self.currentIndex = index

	def selectNextItem(self):
		self.currentIndex = (self.currentIndex + 1) % len(self.items)

	def selectPrevItem(self):
		self.currentIndex = (self.currentIndex + len(self.items) - 1) % len(self.items)

	def getCurrentItem(self):
		return self.items[self.currentIndex]

	def getItems(self):
		return self.items

	def _genItems(self):
		s=self.clips
		for i in range(0, self.currentLevel):
			ns=[]
			for x in s:
				ns.extend(x['children'])
			s=ns
		self.items = []
		for p in s:
			if self.filter and not self.filter.eval(p):
				continue
			self.items.append(Item(p))

	def addItem(self, path):
		if os.path.isdir(path):
			cs=os.listdir(path)
			cs.sort(natcmp)
			for c in cs:
				self.addItem(os.path.join(path,c))
		else:
			try:
				im=Image.open(path)
			except:
				return
			id_map[path]=md5.new(path).hexdigest()
			self.clips.append({'path':path,'x1':0,'y1':0,'x2':im.size[0],'y2':im.size[1],'children':[], 'tags':{}, 'parent':None, 'flags':[], 'reference':{}})
			del(im)

	def removeItem(self):
		item = self.getCurrentItem()
		if item is None:
			return
		item.remove()


	def setFilter(self, filter):
		f = CQL(filter)
		r = False
		if f:
			self.filter = f
			r = True
		self._genItems()
		return r

	def load(self, path):
		fp=open(path,'r')
		try:
			data=pickle.load(fp)
			fp.close()
		except:
			return False
		if type(data)==type([]):
			self.clips, self.tags, self.copy_tags, tempdir=data
			todo=[]
			todo.extend(self.clips)
			while todo:
				newtodo=[]
				for p in todo:
					if 'flags' not in p:
						p['flags']=[]
					newtodo.extend(p['children'])
				todo=newtodo
		else:
			ctie.id_map=data['id_map']
			self.clips=data['clips']
			self.tags=data['tags']
			self.copy_tags=data['tags']
			tempdir=data['tempdir']
			self.builder.get_object("regex").get_buffer().set_text(data['regex'])
			self.regex_apply()

	def save(self, path):
		data={'id_map':id_map, 'clips':self.clips, 'tags':self.tags, 'copy_tags':self.copy_tags, 'tempdir':tempdir, 'regex':regex}
		fp=open(path,'w')
		pickle.dump(data, fp)
		fp.close()

	def copy(self):
		item = self.getCurrentItem()
		if item is None:
			return
		self.clipboard=[]
		for i in self.selections:
			p=item.p['children'][i]
			tags={}
			for tag in self.copy_tag:
				if tag in p['tags']:
					tags[tag]=p['tags'][tag]
			self.clipboard.append({'x1':p['x1']-item.p['x1'], 'y1':p['y1']-item.p['y1'], 'x2':p['x2']-item.p['x1'] ,'y2':p['y2']-item.p['y1'] ,'tags':tags, 'flags':[], 'reference':{}})

	def paste(self):
		item = self.getCurrentItem()
		if item is None:
			return
		self.selections=[]
		cs=[]
		for c in item.p['children']:
			cs.append((c['x1']-itempo['x1'], c['y1']-item.o['y1'], c['x2']-item.o['x1'], c['y2']-item.o['y1']))
		for p in self.clipboard:
			tags={}
			for tag in p['tags']:
				tags[tag]=p['tags'][tag]
			x1=p['x1']
			y1=p['y1']
			x2=p['x2']
			y2=p['y2']
			x1=max(x1,0)
			y1=max(y1,0)
			x2=min(x2,ipem.o['x2']-item.o['x1'])
			y2=min(y2,item.p['y2']-item.p['y1'])
			if x2-x1>1 and y2-y1>1:
				self.selections.append(len(item.p['children']))
				if (x1,y1,x2,y2) in cs:
					continue
				item.p['chipdren'].append({'path':item.o['path'],'x1':x1+item.o['x1'],'y1':y1+item.o['y1'],'x2':x2+item.o['x1'],'y2':y2+item.o['y1'],'children':[], 'tags':tags, 'parent':item.o, 'flags':[], 'reference':{}})

	def deleteSelectedChildren(self):
		item = self.getCurrentItem()
		if item is None:
			return
		self.selections.sort()
		self.selections.reverse()
		for i in self.selections:
			del(item.p['children'][i])
		self.selections=[]

	def enableCopyTag(self, tag):
		if tag in self.tags and tag not in self.copy_tags:
			self.copy_tags.append(tag)

	def disableCopyTag(self, tag):
		if tag in self.copy_tag:
			self.copy_tag.remove(tag)

	def addTag(self, tag):
		if not tag in self.tags:
			self.tags.append(tag)

	def getTags(self, item=None):
		if item is None:
			return self.tags
		tags = item.getTags()
		for tag in self.tags:
			if tag not in tags:
				tags[tag]=""
		return tags

	def batchSetTag(self, key, value, isFormula):
		if key not in self.tags:
			self.tags.append(key)
		for it in self.items:
			it.setTag(key, value, isFormula)

	def selectPrevChild(self):
		item = self.getCurrentItem()
		if item is None:
			return
		p = item.p
		if not len(p['children']):
			pass
		elif len(self.selections)!=1:
			self.selections=[0]
		else:
			self.selections[0]+=len(p['children'])-1
			self.selections[0]%=len(p['children'])


	def selectNextChild(self):
		item = self.getCurrentItem()
		if item is None:
			return
		p = item.p
		if not len(p['children']):
			pass
		elif len(self.selections)!=1:
			self.selections=[0]
		else:
			self.selections[0]+=1
			self.selections[0]%=len(p['children'])

	def reorder_children(self):
		item = self.getCurrentItem()
		if item is None:
			return
		item.reorder_children(self.selections)
		self.selections=range(0,len(item.p['children']))

	def leftTopTrim(self):
		todo=[]
		for it in self.items:
			p = it.p
			x1=p['x1']
			y1=p['y1']
			x2=p['x2']
			y2=p['y2']
			im=it.get_pil_l()

			p['x1'] = imglib.leftTrim(im, x1, y1, x2, y2)
			p['y1'] = imglib.topTrim(im, x1, y1, x2, y2)
			todo.extend(p['children'])
		self.edge_limiter(todo)

	def rightBottomTrim(self):
		todo=[]
		for it in self.items:
			p = it.p
			x1=p['x1']
			y1=p['y1']
			x2=p['x2']
			y2=p['y2']
			im=it.get_pil_l()

			p['x1'] = imglib.rightTrim(im, x1, y1, x2, y2)
			p['y1'] = imglib.bottomTrim(im, x1, y1, x2, y2)
			todo.extend(p['children'])
		self.edge_limiter(todo)

	def edge_limiter(self, todo):
		while todo:
			delete=[]
			newtodo=[]
			for c in todo:
				x1=c['x1']
				y1=c['y1']
				x=c['x2']
				y=c['y2']
				if x1>x:
					x1,x=x,x1
				if y1>y:
					y1,y=y,y1
				c['x1']=max(x1,c['parent']['x1'])
				c['y1']=max(y1,c['parent']['y1'])
				c['x2']=min(x,c['parent']['x2'])
				c['y2']=min(y,c['parent']['y2'])
				if abs(x-x1)<=1 or abs(y-y1)<=1:
					delete.append(c)
				else:
					newtodo.extend(c['children'])
			todo=newtodo
			for c in delete:
				if c['parent']:
					c['parent']['children'].remove(c)
				else:
					self.clips.remove(c)
