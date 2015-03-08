"""
 Copyright (c) 2012-2015 Kuan-Chung Chiu <buganini@gmail.com>

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

import re

class CQL(object):
	def __init__(self, i):
		self.loaded=False
		self.tree=False
		if not i:
			return
		if type(i)!=type([]):
			try:
				tokens=re.findall(r"""(&&|\|\||!=|==|>=|<=|>|<|[\$@%#]\{.+?\}|(?:"[^"]*\\(?:.[^"]*\\)*.[^"]*")|(?:"[^"]*")|(?:'[^']*\\(?:.[^']*\\)*.[^']*')|(?:'[^']*')|\+|-+|!|\(|\)|\[|\]|[A-Za-z_]\w*|\d+|,)""",i)
			except:
				return
			self.tree=self.parse(tokens)
		else:
			self.tree=self.parse(i)

	def parse(self, tokens):
		level=0
		stack=[]
		sep=0
		end=len(tokens)
		for i,t in enumerate(tokens):
			if t=='(':
				if not stack and level<=1:
					sep=i
					level=1
				stack.append(')')
			elif t=='[':
				if not stack and level<=1:
					sep=i
					level=1
				stack.append(']')
			elif t in (')',']'):
				if stack and t==stack[-1]:
					end=i
					stack.pop()
				else:
					return
			if stack:
				continue

			if level<=6 and t in ('&&', '||'):
				sep=i
				level=6
			elif level<=5 and t in ('==', '!=','>=','<=','>','<'):
				sep=i
				level=5
			elif level<=4 and t==',':
				sep=i
				level=4
			elif level<=3 and ( t=='+' or re.match('^-+$', t) ):
				sep=i
				level=3
			elif level<=2 and ( t in ('!') or  re.match('^[A-Za-z]\w*$', t) ):
				sep=i
				level=2
			elif level<=1 and ((len(t)>3 and t[0] in ('$','@','%','#') and t[1]=='{' and t[-1]=='}') or (t[0]==t[-1] and t[0] in ("'", '"'))):
				sep=i
				level=1

		if sep<0:
			return
		self.lval=None
		self.rval=None
		t=self.op=tokens[sep]
		if (len(t)>3 and t[0] in ('$','@','%','#') and t[1]=='{' and t[-1]=='}') or (t[0]==t[-1] and t[0] in ("'", '"')):
			pass
		elif re.match('^\d+$',t):
			pass
		elif t=='(':
			self.op='='
			self.rval=CQL(tokens[sep+1:end])
		elif t=='[':
			self.op='[]'
			self.lval=CQL(tokens[0:sep])
			self.rval=CQL(tokens[sep+1:end])
		elif t in ('!','=') or re.match('^[A-Za-z]\w*$',t):
			self.rval=CQL(tokens[sep+1:])
		elif re.match('^-+$', t):
			self.lval=CQL(tokens[0:sep])
			if self.lval!=None and not self.lval:
				self.lval=None
			self.rval=CQL(tokens[sep+1:])
		else:
			self.lval=CQL(tokens[0:sep])
			self.rval=CQL(tokens[sep+1:])
		self.loaded=True
		if self.lval!=None and not self.lval:
			self.loaded=False
		if self.rval!=None and not self.rval:
			self.loaded=False

	def __nonzero__(self):
		return self.loaded

	def __bool__(self):
		return self.loaded

	def eval(self, p):
		if not self.loaded:
			return None
		t=self.op
		if re.match('^\d+$',t):
			return int(t)
		if (t[0]==t[-1] and t[0] in ("'", '"')):
			return eval(t)
		if (len(t)>3 and t[0] in ('$','@','%','#') and t[1]=='{' and t[-1]=='}'):
			key=t[2:-1]
			if t[0]=='$':
				try:
					return p['tags'][key]
				except:
					return ""
			elif t[0]=='@':
				t=p
				r=""
				while not r and t:
					try:
						r=t['tags'][key]
					except:
						r=""
					t=t['parent']
				return r
			elif t[0]=='#':
				r=[]
				for c in p['children']:
					try:
						r.append(c['tags'][key])
					except:
						r.append('')
				return tuple(r)
			elif t[0]=='%':
				k=t[2:-1].upper()
				if k=='COUNT':
					return len(p['children'])
				elif k=='LEVEL':
					t=p['parent']
					r=0
					while t:
						r+=1
						t=t['parent']
					return r
				elif k=='FILE':
					return p['path']
				elif k=='IMAGE':
					it=Item(p)
					return it.get_pil_cropped()
				elif k=='WIDTH':
					return p['x2']-p['x1']
				elif k=='HEIGHT':
					return p['y2']-p['y1']
				elif k=='ORDER':
					if not p['children']:
						return True
					curr=(0,0)
					trace=[curr]
					last=p['children'][0]
					for i in xrange(1,len(p['children'])):
						c=p['children'][i]
						x=c['x1']+c['x2']/2.0
						if x<last['x1']:
							x=-1
						elif x>=last['x2']:
							x=1
						else:
							x=0
						y=c['y1']+c['y2']/2.0
						if y<last['y1']:
							y=-1
						elif y>=last['y2']:
							y=1
						else:
							y=0
						curr=(curr[0]+x, curr[1]+y)
						if curr in trace:
							return False
						# if y<0:
						# 	return False
						trace.append(curr)
						last=c
					return True
				elif k=='INDEX':
					if p['parent']:
						return p['parent']['children'].index(p)+1
					else:
						return 0
				elif k=='UUID':
					return str(uuid.uuid4())
		rval=self.rval.eval(p)
		if re.match('^-+$', t):
			if type(rval)!=int:
				return None
			if self.lval!=None:
				lval=self.lval.eval(p)
				if type(lval)!=int:
					return None
			else:
				lval=0
			if len(t) % 2 == 0:
				return lval+rval
			return lval-rval
		if t=='!':
			return not rval
		if t=='=':
			if type(rval)==type([]):
				return tuple(rval)
			else:
				return rval
		if re.match('^[A-Za-z_]\w*$', t):
			t=t.upper()
			if t=='ABS':
				return abs(rval)
			elif t=='JOIN':
				if(type(rval[0])==unicode):
					s=rval[0].encode("utf-8")
				else:
					s=rval[0]
				a=[x.encode("utf-8") if type(x)==unicode else x for x in rval[1]]
				return s.join(a)
			elif t=='BASENAME':
				return os.path.basename(rval)
			elif t=='DIRNAME':
				return os.path.dirname(rval)
			elif t=='PREFIX':
				return os.path.splitext(rval)[0]
			elif t=='SUFFIX':
				return os.path.splitext(rval)[1]
			elif t=='PATHJOIN':
				return os.path.join(rval[0], rval[1])
			elif t=='LIST_HAS':
				return rval[1] in rval[0]
			else:
				return None
		lval=self.lval.eval(p)
		if t=='[]':
			return lval[rval]
		if t==',':
			if type(lval)==type([]):
				lval.append(rval)
				return lval
			else:
				return [lval,rval]
		if t=='+':
			if(type(lval)==str or type(rval)==str):
				return str(lval)+str(rval)
			return lval+rval
		if t=='==':
			return lval == rval

		if t=='!=':
			return lval != rval
		if t=='&&':
			return lval and rval
		if t=='||':
			return lval or rval
		if t=='>=':
			return lval >= rval
		if t=='<=':
			return lval <= rval
		if t=='>':
			return lval > rval
		if t=='<':
			return lval < rval
