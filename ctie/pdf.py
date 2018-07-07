"""
 Copyright (c) 2014-2015 Kuan-Chung Chiu <buganini@gmail.com>

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
import sys
import subprocess
import re
from table import Table
from ranges import CRanges
import utils
import PIL.Image
import io
import functools

xpdfimport = "./xpdfimport"

class Image:
	def __init__(self, blob, extension):
		self.blob = blob
		self.extension = extension

	def save(self, path):
		f=open(path, "wb")
		f.write(self.blob)
		f.close()
		return True

class PILImage:
	def __init__(self, im, extension):
		self.im = im
		self.extension = extension

	def save(self, path):
		self.im.save(path)
		return True

class DummyImage:
	extension = "null"

	def save(self, path):
		return False

class Line:
	def __init__(self,s):
		self.s_orig=str(s)
		self.s=s

	def __nonzero__(self):
		return bool(self.s)

	def unshift(self, token):
		if token is None:
			return
		self.s = token + " " + self.s

	def splitToken(self):
		try:
			a, b = re.match("^(.[^ ]*) ?(.*)$", self.s).groups()
			return a, b
		except:
			return None, self.s

	def readToken(self):
		r, self.s = self.splitToken()
		return r

	def peekToken(self):
		return self.splitToken()[0]

	def readStr(self):
		s = self.readToken()
		r = []
		escape = False
		for c in s:
			if escape:
				escape = False
				if c == "\\":
					r.append("\\")
				elif c == "r":
					r.append("\r")
				elif c == "n":
					r.append("\n")
				else:
					r.append("\\")
					r.append(c)
			else:
				if c == "\\":
					escape = True
				else:
					r.append(c)
		return "".join(r)

	def readFloat(self):
		return float(self.readToken())

	def readInt(self):
		return int(self.readToken())

	def readBool(self):
		return self.readToken()=="1"

	def __str__(self):
		return "{} / {}".format(self.s, self.s_orig)

def charsToText(charsMap):
	s=[]
	ks=sorted(charsMap.keys(), key = lambda x: (x[1], x[0], x[3], x[2]))
	lastk = (-1, -1, -1, -1) # y1, x1, y2, x2
	for k in ks:
		if lastk[1]>=1 and lastk[1]!=k[1]:
			s.append("\n")
		elif k[0] - lastk[2] > 70:
			s.append(" ")
		lastk = k
		s.append(charsMap[k])
	s="".join(s).split("\n")
	for j in range(len(s)):
		s[j]=s[j].rstrip()
	s="\n".join(s)
	return s.replace("\n\n", "\n").replace("\n\n", "\n").strip()


def translate(m, x, y):
	xp = m[0]*x + m[2]*y + m[4]
	yp = m[1]*x + m[3]*y + m[5]
	return xp, yp

def getImage(file, page, bx1, by1, bx2, by2):
	content = _getContent(file, page, bx1, by1, bx2, by2)
	imgs = content[1]

	fmtmap={"JPEG":"jpg"}

	if len(imgs) == 0:
		return DummyImage()

	if len(imgs) == 1:
		bf=open("blob", "rb")
		offset, size, fmt, x1, y1, x2, y2 = imgs[0]
		bf.seek(offset)
		blob=bf.read(size)
		bf.close()
		return Image(blob, fmtmap.get(fmt, fmt.lower()))

	ims = []
	mx1 = None
	my1 = None
	mx2 = None
	my2 = None
	ws = None
	hs = None
	bf=open("blob", "rb")
	for offset, size, fmt, x1, y1, x2, y2 in imgs:
		bf.seek(offset)
		pfile = io.BytesIO()
		pfile.write(bf.read(size))
		pfile.flush()
		pfile.seek(0)
		im = PIL.Image.open(pfile)
		ims.append((im, x1, y1, x2, y2))
		if ws is None:
			fw = x2 - x1
			fh = y2 - y1
			w, h = im.size
			ws = w/fw
			hs = h/fh
		if mx1 is None:
			mx1 = x1
		else:
			mx1 = min(mx1, x1)
		if my1 is None:
			my1 = y1
		else:
			my1 = min(my1, y1)
		if mx2 is None:
			mx2 = x2
		else:
			mx2 = max(mx2, x2)
		if my2 is None:
			my2 = y2
		else:
			my2 = max(my2, y2)
	bf.close()
	gim = PIL.Image.new("RGB", (int((mx2-mx1)*ws), int((my2-my1)*hs)))
	for im, x1, y1, x2, y2 in ims:
		rw, rh = im.size
		iw = round((x2-x1)*ws)
		ih = round((y2-y1)*hs)
		if rw != iw and rh != ih:
			print("resize", rw, rh, iw, ih)
			im = im.resize((iw, ih), PIL.Image.BICUBIC)
		gim.paste(im, (round((x1-mx1)*ws), round((y1-my1)*hs)))
	ret = PILImage(gim, "png")
	return ret

def getText(file, page, bx1, by1, bx2, by2):
	content = _getContent(file, page, bx1, by1, bx2, by2)
	return content[0]

def getPageSize(file, page):
	sizes = getPageSizes(file)
	if 0 <= page and page < len(sizes):
		return sizes[page]
	return -1, -1

@functools.lru_cache(maxsize=4)
def getPageSizes(file):
	pdf=subprocess.Popen([xpdfimport,"-f","blob",file,"errdoc.pdf"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

	pdf.stdin.write(b"\n")
	pdf.stdin.flush()

	ret = []

	end = False
	while True:
		#pager
		cmd_queue=[]
		while True:
			try:
				ls = pdf.stdout.readline().decode("utf-8").rstrip("\r\n")
				if not ls:
					end = True
					break
			except :
				end=True
				break
			l = Line(ls)
			cmd = l.readToken()
			if cmd=='startPage':
				page_width = l.readFloat()
				page_height = l.readFloat()
				ret.append((page_width, page_height))
		if end:
			break
	return ret

def _getContent(file, page, bx1, by1, bx2, by2):
	pdf=subprocess.Popen([xpdfimport,"-f","blob",file,"errdoc.pdf"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

	pdf.stdin.write(b"\n")
	pdf.stdin.flush()

	pagen=-1
	page_width=0
	page_height=0

	text = {}
	imgs = []

	ctm=[]
	blobOffset = 0
	end = False
	while True:
		#pager
		cmd_queue=[]
		while True:
			try:
				ls = pdf.stdout.readline().decode("utf-8").rstrip("\r\n")
				if not ls:
					end = True
					break
			except :
				end=True
				break
			l = Line(ls)
			cmd = l.readToken()
			if cmd=='startPage':
				pagen += 1
				page_width = l.readFloat()
				page_height = l.readFloat()
				ctm=[(1, 0, 0, 1, 0, 0)]
			elif cmd=='endPage':
				if pagen==page:
					end=True
			elif cmd=="drawChar":
				if pagen!=page:
					continue
				x1 = l.readFloat()
				y1 = l.readFloat()
				x2 = l.readFloat()
				y2 = l.readFloat()
				m00 = l.readFloat()
				m01 = l.readFloat()
				m10 = l.readFloat()
				m11 = l.readFloat()
				fontSize = l.readFloat()
				m = (m00, m01, m10, m11, 0, 0)
				# x1, y1 = translate(m, x1, y1)
				# x2, y2 = translate(m, x2, y2)
				x1, y1 = translate(ctm[-1], x1, y1)
				x2, y2 = translate(ctm[-1], x2, y2)

				x1, x2 = utils.asc(x1, x2)
				y1, y2 = utils.asc(y1, y2)

				c = l.readStr()
				if x1>=bx1 and y1>=by1 and x2<=bx2 and y2<=by2:
					text[(x1,y1,x2,y2)]=c
			elif cmd=="drawImage":
				width = l.readInt()
				height = l.readInt()
				maskBufSize = l.readInt()
				blobOffset += maskBufSize
				fmt = l.readToken()
				bufSize = l.readInt()
				m = (1.0/width, 0, 0, -1.0/height, 0, 1)
				x1, y1 = translate(m, 0, 0)
				x2, y2 = translate(m, width, height)
				x1, y1 = translate(ctm[-1], x1, y1)
				x2, y2 = translate(ctm[-1], x2, y2)

				x1, x2 = utils.asc(x1, x2)
				y1, y2 = utils.asc(y1, y2)

				if pagen==page:
					intersect = utils.intersect(x1, y1, x2, y2, bx1, by1, bx2, by2)
					if intersect and utils.dimension(*intersect)/utils.dimension(x1, y1, x2, y2) > 0.8:
						imgs.append((blobOffset, bufSize, fmt, x1, y1, x2, y2))
				blobOffset += bufSize
			elif cmd=="updateFont":
				fid = l.readInt()
				isEmbedded = l.readInt()
				isBold = l.readInt()
				isItalic = l.readInt()
				isUnderline = l.readInt()
				fs = l.readFloat()
				sz = l.readInt()
				fname = l.readToken()
				blobOffset += sz
			elif cmd=="updateCtm":
				m0 = l.readFloat()
				m1 = l.readFloat()
				m2 = l.readFloat()
				m3 = l.readFloat()
				m4 = l.readFloat()
				m5 = l.readFloat()
				ctm[-1] = (m0, m1, m2, m3, m4, m5)
			elif cmd=="saveState":
				ctm.append(ctm[-1])
			elif cmd=="restoreState":
				ctm.pop()
		if end:
			break

	text = charsToText(text)

	return (text, imgs)

def getTable(file, page, bx1, by1, bx2, by2, rSep=[], cSep=[]):
	pdf=subprocess.Popen([xpdfimport,"-f","blob",file,"errdoc.pdf"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

	pdf.stdin.write(b"\n")
	pdf.stdin.flush()

	pagen=-1
	page_width=0
	page_height=0

	vsep = {}
	hsep = {}
	text = {}

	ctm=[]
	blobOffset = 0
	end = False
	while True:
		#pager
		cmd_queue=[]
		while True:
			try:
				ls = pdf.stdout.readline().decode("utf-8").rstrip("\r\n")
				if not ls:
					end = True
					break
			except :
				end=True
				break
			l = Line(ls)
			cmd = l.readToken()
			if cmd=='startPage':
				pagen += 1
				page_width = l.readFloat()
				page_height = l.readFloat()
				ctm=[(1, 0, 0, 1, 0, 0)]
			elif cmd=='endPage':
				if pagen==page:
					end=True
			elif cmd=="updateFont":
				fid = l.readInt()
				isEmbedded = l.readInt()
				isBold = l.readInt()
				isItalic = l.readInt()
				isUnderline = l.readInt()
				fs = l.readFloat()
				sz = l.readInt()
				fname = l.readToken()
				blobOffset += sz
			elif cmd=="updateCtm":
				m0 = l.readFloat()
				m1 = l.readFloat()
				m2 = l.readFloat()
				m3 = l.readFloat()
				m4 = l.readFloat()
				m5 = l.readFloat()
				ctm[-1] = (m0, m1, m2, m3, m4, m5)
			elif cmd=="saveState":
				ctm.append(ctm[-1])
			elif cmd=="restoreState":
				ctm.pop()
			elif cmd=="drawChar":
				if pagen!=page:
					continue
				x1 = l.readFloat()
				y1 = l.readFloat()
				x2 = l.readFloat()
				y2 = l.readFloat()
				m00 = l.readFloat()
				m01 = l.readFloat()
				m10 = l.readFloat()
				m11 = l.readFloat()
				fontSize = l.readFloat()
				m = (m00, m01, m10, m11, 0, 0)
				# x1, y1 = translate(m, x1, y1)
				# x2, y2 = translate(m, x2, y2)
				x1, y1 = translate(ctm[-1], x1, y1)
				x2, y2 = translate(ctm[-1], x2, y2)

				x1, x2 = utils.asc(x1, x2)
				y1, y2 = utils.asc(y1, y2)

				c = l.readStr()
				if x1>=bx1 and y1>=by1 and x2<=bx2 and y2<=by2:
					text[(x1,y1,x2,y2)]=c
			elif cmd in ("strokePath", "fillPath", "eoFillPath"):
				if pagen!=page or (rSep and cSep):
					continue
				pts = []
				while l:
					token = l.readToken()
					if token == "subpath":
						isBorder = True
						closed_flag = l.readBool()
						ps = []
					else:
						l.unshift(token)
						if ps and isBorder:
							pts.append(ps)

					try:
						x = l.readFloat()
						y = l.readFloat()
						curve = l.readBool()
						if curve:
							isBorder = False
							break
						x, y = translate(ctm[-1], x, y)
						ps.append((x,y))
					except:
						break

				if ps and isBorder:
					pts.append(ps)

				for ps in pts:
					for i in range(len(ps)-1):
						if ps[i][0] == ps[i+1][0]:
							if bx1 <= ps[i][0] and ps[i][0] <= bx2:
								if ps[i][0] not in vsep:
									vsep[ps[i][0]] = CRanges()
								vsep[ps[i][0]].add(ps[i][1], ps[i+1][1])
						elif ps[i][1] == ps[i+1][1]:
							if by1 <= ps[i][1] and ps[i][1] <= by2:
								if ps[i][1] not in hsep:
									hsep[ps[i][1]] = CRanges()
								hsep[ps[i][1]].add(ps[i][0], ps[i+1][0])
		if end:
			break

	if cSep and rSep:
		cSep.insert(0, 0)
		cSep.append(bx2)
		rSep.insert(0, 0)
		rSep.append(by2)
	else:
		vsepPos = list(vsep.keys())
		vsepPos.sort()
		hsepPos = list(hsep.keys())
		hsepPos.sort()

	textmap = {}

	for rect in text:
		x1,y1,x2,y2 = rect
		row = -1
		col = -1
		c = text[rect]
		if cSep and rSep:
			for i in range(len(rSep)):
				if y1 < rSep[i]+by1:
					row = i
					break
			for i in range(len(cSep)):
				if x1 < cSep[i]+bx1:
					col = i
					break
		else:
			for i in range(len(hsepPos)):
				if y1 < hsepPos[i] and hsep[hsepPos[i]].contains(x1) > 1:
					row = i
					break
			for i in range(len(vsepPos)):
				if x1 < vsepPos[i] and vsep[vsepPos[i]].contains(y1) > 1:
					col = i
					break
		pos = (row, col)
		if pos not in textmap:
			textmap[pos] = {}
		textmap[pos][rect] = c

	rs = []
	cs = []

	for pos in textmap:
		r, c = pos
		if r not in rs:
			rs.append(r)
		if c not in cs:
			cs.append(c)

	rs.sort()
	cs.sort()

	rmap = {}
	cmap = {}
	for i,r in enumerate(rs):
		rmap[r]=i
	for i,c in enumerate(cs):
		cmap[c]=i

	table = Table()

	for pos in textmap:
		table.set(rmap[pos[0]], cmap[pos[1]], charsToText(textmap[pos]))

	return table

def getLines(file, page, bx1, by1, bx2, by2):
	pdf=subprocess.Popen([xpdfimport,"-f","blob",file,"errdoc.pdf"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

	pdf.stdin.write(b"\n")
	pdf.stdin.flush()

	pagen=-1

	vsep = {}
	hsep = {}
	polygons = []

	ctm=[]
	end = False
	contentBounds = []
	while True:
		#pager
		cmd_queue=[]
		while True:
			try:
				ls = pdf.stdout.readline().decode("utf-8").rstrip("\r\n")
				if not ls:
					end = True
					break
			except :
				end=True
				break
			l = Line(ls)
			cmd = l.readToken()
			if cmd=='startPage':
				pagen += 1
				ctm=[(1, 0, 0, 1, 0, 0)]
			elif cmd=='endPage':
				if pagen==page:
					end=True
			elif cmd=="updateCtm":
				m0 = l.readFloat()
				m1 = l.readFloat()
				m2 = l.readFloat()
				m3 = l.readFloat()
				m4 = l.readFloat()
				m5 = l.readFloat()
				ctm[-1] = (m0, m1, m2, m3, m4, m5)
			elif cmd=="saveState":
				ctm.append(ctm[-1])
			elif cmd=="restoreState":
				ctm.pop()
			elif cmd=="drawChar":
				if pagen!=page:
					continue
				x1 = l.readFloat()
				y1 = l.readFloat()
				x2 = l.readFloat()
				y2 = l.readFloat()
				m00 = l.readFloat()
				m01 = l.readFloat()
				m10 = l.readFloat()
				m11 = l.readFloat()
				fontSize = l.readFloat()
				m = (m00, m01, m10, m11, 0, 0)
				# x1, y1 = translate(m, x1, y1)
				# x2, y2 = translate(m, x2, y2)
				x1, y1 = translate(ctm[-1], x1, y1)
				x2, y2 = translate(ctm[-1], x2, y2)

				x1, x2 = utils.asc(x1, x2)
				y1, y2 = utils.asc(y1, y2)
				contentBounds.append((x1, y1, x2, y2))
			elif cmd=="drawImage":
				width = l.readInt()
				height = l.readInt()
				maskBufSize = l.readInt()
				fmt = l.readToken()
				bufSize = l.readInt()
				m = (1.0/width, 0, 0, -1.0/height, 0, 1)
				x1, y1 = translate(m, 0, 0)
				x2, y2 = translate(m, width, height)
				x1, y1 = translate(ctm[-1], x1, y1)
				x2, y2 = translate(ctm[-1], x2, y2)

				x1, x2 = utils.asc(x1, x2)
				y1, y2 = utils.asc(y1, y2)

				# contentBounds.append((x1, y1, x2, y2))
			elif cmd in ("strokePath", "fillPath", "eoFillPath"):
				if pagen!=page:
					continue
				pts = []
				while l:
					token = l.readToken()
					if token == "subpath":
						isBorder = True
						closed_flag = l.readBool()
						ps = []
					else:
						l.unshift(token)
						if ps and isBorder:
							pts.extend(ps)
					try:
						x = l.readFloat()
						y = l.readFloat()
						curve = l.readBool()
						if curve:
							isBorder = False
							break
						x, y = translate(ctm[-1], x, y)
						ps.append((x,y))
					except:
						break

				if ps and isBorder:
					pts.extend(ps)

				polygons.append(pts)
		if end:
			break

	vsep = []
	hsep = []
	for ps in polygons:
		minx = min([p[0] for p in ps])
		miny = min([p[1] for p in ps])
		maxx = max([p[0] for p in ps])
		maxy = max([p[1] for p in ps])

		if not utils.intersect(minx, miny, maxx, maxy, bx1, by1, bx2, by2):
			continue

		hasContent = False
		for pos in contentBounds:
			if utils.intersect(minx, miny, maxx, maxy, pos[0], pos[1], pos[2], pos[3]):
				hasContent = True
				break

		if hasContent:
			continue

		dx = maxx - minx
		dy = maxy - miny
		if dx == 0 or dy == 0:
			continue

		if dx > dy:
			hsep.append(miny)
		elif dx < dy:
			vsep.append(minx)

	return sorted(vsep), sorted(hsep)
