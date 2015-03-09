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
		self.currentLevel = level
		self._genItems()

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
			self.clips, self.tags, self.copy_tag, tempdir=data
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
			self.copy_tag=data['tags']
			tempdir=data['tempdir']
			self.builder.get_object("regex").get_buffer().set_text(data['regex'])
			self.regex_apply()

	def save(self, path):
		data={'id_map':id_map, 'clips':self.clips, 'tags':self.tags, 'copy_tags':self.copy_tag, 'tempdir':tempdir, 'regex':regex}
		fp=open(path,'w')
		pickle.dump(data, fp)
		fp.close()

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
			p=it.p
			if formula:
				p["tags"][key]=formula.eval(p)
			else:
				p["tags"][key]=value

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
