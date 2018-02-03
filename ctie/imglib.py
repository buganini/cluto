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
default_threshold = 30
default_margin = 5

def leftTrim(im, x1, y1, x2, y2, margin=default_margin, threshold=default_threshold):
	stop=False
	for a in range(x1,x2):
		last=im.getpixel((a,y1))
		for i in range(y1,y2):
			c=im.getpixel((a,i))
			if abs(c-last)>threshold:
				stop=True
				break
			last=c
		if stop:
			break
	nx1=a-margin
	return max(nx1,x1)

def rightTrim(im, x1, y1, x2, y2, margin=default_margin, threshold=default_threshold):
	stop=False
	for a in range(x2,x1,-1):
		last=im.getpixel((a-1,y1))
		for i in range(y1,y2):
			c=im.getpixel((a-1,i))
			if abs(c-last)>threshold:
				stop=True
				break
			last=c
		if stop:
			break
	nx2=a+margin
	return min(nx2, x2)

def topTrim(im, x1, y1, x2, y2, margin=default_margin, threshold=default_threshold):
	stop=False
	for a in range(y1,y2):
		last=im.getpixel((x1,a))
		for i in range(x1,x2):
			c=im.getpixel((i,a))
			if abs(c-last)>threshold:
				stop=True
				break
			last=c
		if stop:
			break
	ny1=a-margin
	return max(ny1,y1)

def bottomTrim(im, x1, y1, x2, y2, margin=default_margin, threshold=default_threshold):
	stop=False
	for a in range(y2,y1,-1):
		last=im.getpixel((x1,a-1))
		for i in range(x1,x2):
			c=im.getpixel((i,a-1))
			if abs(c-last)>threshold:
				stop=True
				break
			last=c
		if stop:
			break
	ny2=a+margin
	return min(ny2, y2)
