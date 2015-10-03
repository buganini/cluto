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

class Image:
	def __init__(self, blob, extension):
		self.blob = blob
		self.extension = extension

	def save(self, path):
		f=open(path, "w")
		f.write(self.blob)
		f.close()

class Line:
	def __init__(self,s):
		self.s_orig=str(s)
		self.s=s

	def __nonzero__(self):
		return bool(self.s)

	def unshift(self, token):
		self.s = token + " " + self.s

	def readToken(self):
		try:
			r, self.s = re.match("^(.[^ ]*) ?(.*)$", self.s).groups()
			return r
		except:
			return ''

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
		return self.s_orig

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

	ret = None
	bf=open("blob", "r")
	fmtmap={"JPEG":"jpg"}
	for offset, size, fmt, x1, y1, x2, y2 in imgs[0:1]:
		bf.seek(offset)
		blob=bf.read(size)
		ret = Image(blob, fmtmap.get(fmt, fmt.lower()))
	bf.close()
	return ret

def getText(file, page, bx1, by1, bx2, by2):
	content = _getContent(file, page, bx1, by1, bx2, by2)
	return content[0]

def _getContent(file, page, bx1, by1, bx2, by2):
	pdf=subprocess.Popen(["./xpdfimport","-f","blob",file,"errdoc.pdf"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

	pdf.stdin.write("\n")

	pagen=-1
	page_width=0
	page_height=0

	cmds=pdf.stdout.readlines().__iter__()

	text = {}
	imgs = []

	ctm=[]
	sn = 0
	blobOffset = 0
	end = False
	while True:
		#pager
		cmd_queue=[]
		while True:
			try:
				ls = cmds.next().rstrip("\r\n")
			except:
				end=True
				break
			l = Line(ls)
			cmd = l.readToken()
			if cmd=='setPageNum':
				pagenum = l.readInt()
			elif cmd=='startPage':
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

				c = l.readStr()
				if x1>=bx1 and y1>=by1 and x2<=bx2 and y2<=by2:
					text[(y1,x1,y2,x2)]=c
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
				if pagen==page:
					if x1>=bx1 and y1>=by1 and x2<=bx2 and y2<=by2:
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

	pdf.wait()

	text = charsToText(text)

	return (text, imgs)

def getTable(file, page, bx1, by1, bx2, by2):
	pdf=subprocess.Popen(["./xpdfimport","-f","blob",file,"errdoc.pdf"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

	pdf.stdin.write("\n")

	pagen=-1
	page_width=0
	page_height=0

	cmds=pdf.stdout.readlines().__iter__()

	vsep = {}
	hsep = {}
	text = {}

	ctm=[]
	sn = 0
	blobOffset = 0
	end = False
	while True:
		#pager
		cmd_queue=[]
		while True:
			try:
				ls = cmds.next().rstrip("\r\n")
			except:
				end=True
				break
			l = Line(ls)
			cmd = l.readToken()
			if cmd=='setPageNum':
				pagenum = l.readInt()
			elif cmd=='startPage':
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

				c = l.readStr()
				if x1>=bx1 and y1>=by1 and x2<=bx2 and y2<=by2:
					text[(x1,y1,x2,y2)]=c
			elif cmd in ("strokePath", "fillPath"):
				if pagen!=page:
					continue
				pts = []
				while l:
					token = l.readToken()
					if token == "subpath":
						isBorder = True
						isInside = False
						closed_flag = l.readBool()
						ps = []
					else:
						l.unshift(token)
						if ps and isBorder and isInside:
							pts.append(ps)

					x = l.readFloat()
					y = l.readFloat()
					curve = l.readBool()
					if curve:
						isBorder = False
						break
					x, y = translate(ctm[-1], x, y)
					if x>=bx1 and y>=by1 and x<=bx2 and y<=by2:
						isInside = True
						ps.append((x,y))

				if ps and isBorder and isInside:
					pts.append(ps)

				for ps in pts:
					for i in range(len(ps)-1):
						if ps[i][0] == ps[i+1][0]:
							if ps[i][0] not in vsep:
								vsep[ps[i][0]] = CRanges()
							vsep[ps[i][0]].add(ps[i][1], ps[i+1][1])
						else:
							if ps[i][1] not in hsep:
								hsep[ps[i][1]] = CRanges()
							hsep[ps[i][1]].add(ps[i][0], ps[i+1][0])
		if end:
			break

	pdf.wait()

	vsepPos = vsep.keys()
	vsepPos.sort()
	hsepPos = hsep.keys()
	hsepPos.sort()

	textmap = {}

	for rect in text:
		x1,y1,x2,y2 = rect
		row = -1
		col = -1
		c = text[rect]
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
