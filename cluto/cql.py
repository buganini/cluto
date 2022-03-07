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
import re
import json
import csv
import cluto

__cql_cache__ = {}

class CQL(object):
	def __init__(self, i):
		self.expr = i
		self.loaded = False
		self.tree = False
		if not i:
			return
		if type(i)!=type([]):
			try:
				tokens = re.findall(r"""(&&|\|\||!=|==|>=|<=|>|<|\.|[\$@%#]\{.+?\}|(?:"[^"]*\\(?:.[^"]*\\)*.[^"]*")|(?:"[^"]*")|(?:'[^']*\\(?:.[^']*\\)*.[^']*')|(?:'[^']*')|\+|-+|!|[A-Za-z_]\w*\(|\(|\)|\[|\]|\d+|,)""",i)
			except:
				return
			self.tree = self.parse(tokens)
		else:
			self.tree = self.parse(i)

	def __str__(self):
		return str(self.expr)

	def parse(self, tokens):
		level = 0
		stack = []
		sep = 0
		end = len(tokens)
		for i,t in enumerate(tokens):
			if t=='(':
				if not stack and level<=1:
					sep = i
					level = 1
				stack.append(')')
			elif t=='[':
				if not stack and level<=1:
					sep = i
					level = 1
				stack.append(']')
			elif re.match(r'^[A-Za-z_]\w*\($', t):
				if not stack and level<=1:
					sep = i
					level = 1
				stack.append(')')
			elif t in (')',']'):
				if stack and t==stack[-1]:
					end = i
					stack.pop()
				else:
					return
			if stack:
				continue

			if level <= 7 and t in ('&&', '||'):
				sep = i
				level = 7
			elif level <= 6 and t in ('==', '!=','>=','<=','>','<'):
				sep = i
				level = 6
			elif level <= 5 and t==',':
				sep = i
				level = 5
			elif level <= 4 and t==".":
				sep = i
				level = 4
			elif level <= 3 and ( t=='+' or re.match('^-+$', t) ):
				sep = i
				level = 3
			elif level <= 2 and t=="!":
				sep = i
				level = 2
			elif level <= 1 and ((len(t)>3 and t[0] in ('$','@','%','#') and t[1]=='{' and t[-1]=='}') or (t[0]==t[-1] and t[0] in ("'", '"'))):
				sep = i
				level = 1

		if sep<0:
			return
		self.lval = None
		self.rval = None
		t = self.op = tokens[sep]
		if (len(t)>3 and t[0] in ('$','@','%','#') and t[1]=='{' and t[-1]=='}') or (t[0]==t[-1] and t[0] in ("'", '"')):
			pass
		elif re.match('^\d+$',t):
			pass
		elif t=='(':
			self.op = '='
			self.rval = CQL(tokens[sep+1:end])
		elif t=='[':
			self.op = '[]'
			self.lval = CQL(tokens[0:sep])
			self.rval = CQL(tokens[sep+1:end])
		elif re.match(r'^[A-Za-z_]\w*\($',t):
			self.rval = CQL(tokens[sep+1:end])
		elif t in ('!','='):
			self.rval = CQL(tokens[sep+1:])
		elif re.match('^-+$', t):
			self.lval = CQL(tokens[0:sep])
			if self.lval!=None and not self.lval:
				self.lval = None
			self.rval = CQL(tokens[sep+1:])
		elif t==',':
			self.lval = CQL(tokens[0:sep])
			r = tokens[sep+1:]
			if r:
				self.rval = CQL(r)
			else:
				self.rval = None
		else:
			self.lval = CQL(tokens[0:sep])
			self.rval = CQL(tokens[sep+1:])
		self.loaded = True
		if self.lval!=None and not self.lval:
			self.loaded = False
		if self.rval!=None and not self.rval:
			self.loaded = False

	def __str__(self):
		return "({} {} {})".format(self.op, self.lval, self.rval)

	def __nonzero__(self):
		return self.loaded

	def __bool__(self):
		return self.loaded

	def eval(self, item):
		if not self.loaded:
			return None
		t = self.op
		if re.match('^\d+$',t):
			return int(t)
		if (t[0]==t[-1] and t[0] in ("'", '"')):
			return json.loads(t)
		if (len(t)>3 and t[0] in ('$','@','%','#') and t[1]=='{' and t[-1]=='}'):
			key = t[2:-1]
			if t[0]=='$':
				r = item.getTag(key)
				if r is None:
					r = ""
				return r
			elif t[0]=='@':
				r = item.getTag(key)
				if not r:
					r = item.getTagFromParent(key)
				if r is None:
					r = ""
				return r
			elif t[0]=='#':
				r = []
				for child in item.children:
					r.append(child.tags.get(key, ""))
				return tuple(r)
			elif t[0]=='%':
				k = t[2:-1].upper()
				if k=='COUNT':
					return len(item.children)
				elif k=='LEVEL':
					t = item.parent
					r = 0
					while t:
						r += 1
						t = t.parent
					return r
				elif k=='FILE':
					return item.path
				elif k=='PAGE':
					if hasattr(item, "page"):
						return "{0}".format(item.page)
					else:
						return "0"
				elif k=="TITLE":
					return item.getTitle()
				elif k=='TYPE':
					return item.getType()
				elif k=='THIS':
					return item
				elif k=='PARENT':
					if item:
						return item.parent
					else:
						return None
				elif k=='CONTENT':
					return item.getContent()
				elif k=='WIDTH':
					return item.x2-item.x1
				elif k=='HEIGHT':
					return item.y2-item.y1
				elif k=='ORDER':
					if not item.children:
						return True
					curr = (0,0)
					trace = [curr]
					last = item.children[0]
					for i in range(1,len(item.children)):
						child = item.children[i]
						x = child.x1+child.x2/2.0
						if x<last['x1']:
							x = -1
						elif x>=last['x2']:
							x = 1
						else:
							x = 0
						y = child.y1+child.y2/2.0
						if y<last['y1']:
							y = -1
						elif y>=last['y2']:
							y = 1
						else:
							y = 0
						curr = (curr[0]+x, curr[1]+y)
						if curr in trace:
							return False
						# if y<0:
						# 	return False
						trace.append(curr)
						last = child
					return True
				elif k=='INDEX':
					return item.getIndex()+1
				elif k=='HASH':
					return item.hash
				else:
					print("Unknown attribute", t)
					return None
		if t==".":
			return self.rval.eval(self.lval.eval(item))
		if self.rval is None:
			rval = None
		else:
			rval = self.rval.eval(item)
		if re.match('^-+$', t):
			if type(rval)!=int:
				return None
			if self.lval!=None:
				lval = self.lval.eval(item)
				if type(lval)!=int:
					return None
			else:
				lval = 0
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
		if re.match(r'^[A-Za-z_]\w*\($', t):
			t = t.upper()[:-1]
			if t=='ABS':
				return abs(rval)
			elif t=='TEXT':
				return str(rval)
			elif t=='CHILD':
				return rval[0].children[rval[1]-1]
			elif t=='JOIN':
				s = str(rval[0])
				a = [str(x) for x in rval[1]]
				return s.join(a)
			elif t=='COALESCE':
				for i in rval:
					if i:
						return i
				return ""
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
			elif t=='CONCAT':
				alllist = True
				for i in rval:
					if type(i)!=type([]):
						alllist = False
						break
				if alllist:
					return ["".join(x) for x in zip(*rval)]
				else:
					return "".join(rval)
			elif t=='LIST_HAS':
				return rval[1] in rval[0]
			elif t=='SPLIT':
				return tuple(rval[1].split(rval[0]))
			elif t=='SLICE':
				l = len(rval) - 1
				if l == 1:
					return rval[0][rval[1]:]
				elif l == 2:
					return rval[0][rval[1]:rval[2]]
			elif t=='LEN':
				return len(rval)
			elif t=='REPLACE':
				return rval[2].replace(rval[0], rval[1])
			elif t=='REGEX_REPLACE':
				return re.sub(rval[0], rval[1], rval[2])
			elif t=='FIELD':
				field = rval[0]
				text = rval[1]
				separator = ":"
				if type(field) is str:
					field = [field]
				pat = r"^(?:{fields})[ \t]*[{separator}]+[ \t]*(.*?)\s*$".format(fields="|".join([re.escape(x) for x in field]), separator=separator)
				m = re.findall(pat, text, flags=re.MULTILINE|re.IGNORECASE)
				if m:
					m = [x.strip() for x in m if x.strip()]
					return " ".join(m)
				return ""
			elif t=="REJECT":
				blacklist = rval[0]
				text = rval[1]
				return "\n".join([x for x in text.split("\n") if x not in blacklist])
			elif t=="REJECT_FIELD":
				field = rval[0]
				text = rval[1]
				separator = ":"
				if type(field) is str:
					field = [field]
				pat = re.compile(r"^(?:{fields})[ \t]*[{separator}]+[ \t]*(.*?)\s*$".format(fields="|".join([re.escape(x) for x in field]), separator=separator))
				return "\n".join([x for x in text.split("\n") if not pat.match(x)])
			elif t=='LOOKUP':
				tablefn = rval[0]
				tbkey = "table_"+tablefn
				if not tbkey in __cql_cache__:
					m = {}
					with open(os.path.join(cluto.instance.workspace, tablefn), newline='') as csvfile:
						reader = csv.reader(csvfile)
						for row in reader:
							m[row[0]] = row[1]
					__cql_cache__[tbkey] = m
				table = __cql_cache__[tbkey]
				return table.get(rval[1], "")
			elif t=='ENSURE':
				token = rval[0]
				text = rval[1]
				line = rval[2]
				if re.search(r"\b{}\b".format(re.escape(token)), text, re.IGNORECASE):
					return text
				else:
					lines = text.split("\n")
					if line < len(lines):
						if lines[line]:
							if lines[line][0] in " ":
								lines[line] = token + lines[line]
							else:
								lines[line] = f"{token} {lines[line]}"
						else:
							lines[line] = token
					else:
						lines.append(token)
					return "\n".join(lines)
			elif t=='PRINT':
				print("{}: {}".format(repr(rval), str(rval)))
				return rval
			else:
				print("Unknown function", t)
				return None
		if self.lval is None:
			return rval
		lval = self.lval.eval(item)
		if t=='[]':
			return lval[rval]
		if t==',':
			if type(lval)==type([]):
				lval.append(rval)
				return lval
			else:
				if not rval is None:
					return [lval,rval]
				else:
					return [lval]
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

if __name__=="__main__":
	print(CQL("1,2").eval(None))
	print(CQL("(1,2),(3,4)").eval(None))
	print(CQL("1,").eval(None))