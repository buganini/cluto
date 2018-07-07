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
from PIL import Image
import weakref
import uuid
import os
import utils

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
        self.cache = {}
        if self.path is None:
            self.path = parent.path

        self.hash = str(uuid.uuid4())
        self.listener = []

    def __str__(self):
        return "{0:X} # {1} ({2},{3},{4},{5})".format(id(self), os.path.basename(self.path), self.x1, self.y1, self.x2, self.y2)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['listener']
        del state['cache']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.listener = []
        self.cache = {}

    def resetCache(self):
        self.cache = {}

    def addListener(self, l):
        self.listener.append(l)

    def removeListener(self, l):
        try:
            self.listener.remove(l)
        except:
            pass

    def getFullPath(self):
        return os.path.join(ctie.instance.workspace, self.path)

    def getTitle(self):
        return os.path.basename(self.path)

    def getWorkdir(self):
        path = os.path.join(ctie.instance.tempdir, self.hash)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

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

    def worker(self):
        pass

    def drawQT(self, painter, scale):
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
        for l in self.listener:
            l()

    def getTag(self, key):
        return self.tags.get(key)

    def getTagFromParent(self, key):
        t = self.parent
        r = None
        while r is None and t:
            r = t.tags.get(key, None)
            t = t.parent
        return r

    def unsetTag(self, key):
        del(self.tags[key])
        ctie.ui.onTagChanged()

    def contains(self, x, y):
        return x>self.x1 and x<self.x2 and y>self.y1 and y<self.y2

    def addChild(self, **arg):
        k = self.__class__
        child = k(parent = self, **arg)
        self.children.append(child)
        ctie.instance.ui.onItemTreeChanged()
        ctie.instance.worker.addBgJob(child)
        return child

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

    def batchPaste(self, clipboard, chk_empty, chk_overlap, chk_overlap_aon, chk_boundary, chk_boundary_aon):
        if chk_empty and self.children:
            return

        todo = []
        for p in clipboard:
            x1 = p['x1']
            y1 = p['y1']
            x2 = p['x2']
            y2 = p['y2']
            x1 = max(x1, 0)
            y1 = max(y1, 0)
            x2 = min(x2, self.x2-self.x1)
            y2 = min(y2, self.y2-self.y1)
            x1 = x1 + self.x1
            y1 = y1 + self.y1
            x2 = x2 + self.x1
            y2 = y2 + self.y1
            if x2-x1>1 and y2-y1>1:
                todo.append({'x1':x1, 'y1':y1, 'x2':x2, 'y2':y2, 'tags':p['tags']})

        if chk_overlap:
            newtodo = []
            for p in todo:
                ok = True
                for c in self.children:
                    if utils.rect_overlap(p['x1'], p['y1'], p['x2'], p['y2'], c.x1, c.y1, c.x2, c.y2):
                        ok = False
                        break
                if ok:
                    newtodo.append(p)
                else:
                    if chk_overlap_aon:
                        return
            todo = newtodo

        if chk_boundary:
            newtodo = []
            for p in todo:
                if self.check_boundary(p['x1'], p['y1'], p['x2'], p['y2']):
                    newtodo.append(p)
                else:
                    if chk_boundary_aon:
                        return
            todo = newtodo

        for p in todo:
            self.addChild(x1 = p['x1'], y1 = p['y1'], x2 = p['x2'], y2 = p['y2'], tags = p['tags'])

    def check_boundary(self, x1, y1, x2, y2):
        return True

    def ocr(self):
        pass

    def trim(self, *args):
        pass

    def shrink(self, left, top, right, bottom, amount=0):
        x1 = self.x1
        y1 = self.y1
        x2 = self.x2
        y2 = self.y2

        if left:
            nx1 = x1 + amount
            x1 = min(x2-1, nx1)
        if top:
            ny1 = y1 + amount
            y1 = min(y2-1, ny1)
        if right:
            nx2 = x2 - amount
            x2 = max(x1, nx2)
        if bottom:
            ny2 = y2 - amount
            y2 = max(y1, ny2)

        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2