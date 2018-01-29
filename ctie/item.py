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

from __future__ import division
import os
from PIL import Image
import weakref
import uuid
# from gi.repository import Gtk

import ctie
from cql import *

class Item(object):
    def __init__(self, path = None, parent = None, x1 = 0, y1 = 0, x2 = 0, y2 = 0, tags = {}):
        self.path = path
        self.parent = parent
        self.x1 = int(x1)
        self.y1 = int(y1)
        self.x2 = int(x2)
        self.y2 = int(y2)
        self.children = []
        self.tags = dict(tags)
        if self.path is None:
            self.path = parent.path

        self.hash = str(uuid.uuid4())

    def __str__(self):
        return "{0:X} # {1} ({2},{3},{4},{5})".format(id(self), os.path.basename(self.path), self.x1, self.y1, self.x2, self.y2)

    def getIndex(self):
        if self.parent:
            return self.parent.children.index(self)
        else:
            return ctie.instance.clips.index(self)

    def getTypes(self):
        return False

    def getType(self):
        return self.tags.get("_type", None)

    def setType(self, t):
        self.tags["_type"] = t

    def getExtension(self):
        pass

    def getContent(self):
        pass

    def getSize(self):
        return self.x2-self.x1, self.y2-self.y1

    def getThumbnailSize(self, cw, ch):
        w = self.x2-self.x1
        h = self.y2-self.y1
        wf = cw/w
        hf = ch/h
        if wf < hf:
            sw = cw
            sh = h*wf
            factor = wf
        else:
            sw = w*hf
            sh = ch
            factor = hf
        return sw, sh, factor

    def drawThumbnail(self, widget, cr):
        pass

    def drawThumbnailQT(self, widget, width, height):
        pass

    def draw(self, widget, cr):
        pass

    def getTags(self):
        tags = {}
        t = self
        while t:
            for key in t.tags:
                if key not in tags:
                    tags[key] = t.tags[key]
            t = t.parent
        return tags

    def setTag(self, key, value, isFormula = False):
        if isFormula:
            self.tags[key] = str(CQL(value).eval(self))
        else:
            self.tags[key] = value

    def getTag(self, key):
        return self.tags.get(key)

    def unsetTag(self, key):
        del(self.tags[key])
        ctie.ui.onTagChanged()

    def contains(self, x, y):
        return x>self.x1 and x<self.x2 and y>self.y1 and y<self.y2

    def addChild(self, **arg):
        k = self.__class__
        self.children.append(k(parent = self, **arg))
        ctie.instance.ui.onItemTreeChanged()

    def removeChild(self, child):
        self.children.remove(child)
        ctie.instance.ui.onItemTreeChanged()

    def remove(self):
        ctie.instance.removeItem(self)
        if self.parent:
            self.parent.children.remove(self)
            ctie.instance.ui.onItemTreeChanged()

    def move(self, index, xoff, yoff):
        xoff = int(xoff)
        yoff = int(yoff)
        todo = [self.children[index]]
        while todo:
            delete = []
            newtodo = []
            for c in todo:
                x1 = c.x1+xoff
                y1 = c.y1+yoff
                x = c.x2+xoff
                y = c.y2+yoff
                x1 = max(x1, c.parent.x1)
                y1 = max(y1, c.parent.y1)
                x = min(x, c.parent.x2)
                y = min(y, c.parent.y2)
                c.x1 = min(x1, c.parent.x2)
                c.y1 = min(y1, c.parent.y2)
                c.x2 = max(x, c.parent.x1)
                c.y2 = max(y, c.parent.y1)
                if abs(x-x1)<=1 or abs(y-y1)<=1:
                    delete.append(c)
                else:
                    newtodo.extend(c.children)
            todo = newtodo
            for item in delete:
                item.remove()

    def resize(self, index, xoff, yoff):
        xoff = int(xoff)
        yoff = int(yoff)
        child = self.children[index]
        xoff2 = max(xoff, child.x1-child.x2)
        yoff2 = max(yoff, child.y1-child.y2)
        x1 = child.x1
        y1 = child.y1
        x = child.x2+xoff2
        y = child.y2+yoff2
        child.x1 = max(x1, self.x1)
        child.y1 = max(y1, self.y1)
        child.x2 = min(x, self.x2)
        child.y2 = min(y, self.y2)
        if abs(x-x1)<=1 or abs(y-y1)<=1:
            child.remove()

    def reorder_children(self, ordered_list = []):
        self.children = self.reordered_children(ordered_list)

    def reordered_children(self, ordered_list = []):
        r = []
        for i in ordered_list:
            r.append(self.children[i])
        for i,c in enumerate(self.children):
            if i not in ordered_list:
                r.append(c)
        return r

    def ocr(self):
        pass

    def leftTopTrim(self):
        pass

    def rightBottomTrim(self):
        pass
