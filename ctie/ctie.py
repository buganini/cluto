import os
from gi.repository import Gtk
import Image
import weakref
import math
import md5

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

class Ctie(object):
	def __init__(self, ui, path=None):
		self.regex=[]
		self.clips=[]
		self.tags=[]

	def isEmpty(self):
		return len(self.clips)==0

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
