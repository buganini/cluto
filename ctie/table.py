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

import csv

class Table(object):
	def __init__(self):
		self.data = {}
		self.maxr = -1
		self.maxc = -1

	def __str__(self):
		ret = []
		for r in range(self.maxr+1):
			row = []
			for c in range(self.maxc+1):
				t = self.data.get((r,c), None)
				if not t is None:
					row.append(t)
			ret.append(": ".join(row))
		return "\n".join(ret)

	def set(self, row, col, content):
		self.data[(row, col)] = content
		if row > self.maxr:
			self.maxr = row
		if col > self.maxc:
			self.maxc = col

	def save(self, path):
		fn = path+".csv"
		f = open(fn, "w")
		writer = csv.writer(f)
		for r in range(self.maxr+1):
			row = []
			for c in range(self.maxc+1):
				row.append(self.data.get((r,c), ""))
			writer.writerow(row)
		f.close()
		return fn
