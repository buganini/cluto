"""
 Copyright (c) 2012-2018 Kuan-Chung Chiu <buganini@gmail.com>

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
import pickle
import functools
import html

from imageItem import *
from pdfItem import *
from cql import *
from helpers import *
import pdf
import utils

from worker import WorkerDispatcher

instance = None

class Ctie(object):
    def __init__(self, ui, path = None):
        global instance
        instance = self
        self.ui = ui

        self.worker = WorkerDispatcher(self)

        self.reset()

        pdf.xpdfimport = "/opt/libreoffice5.4/program/xpdfimport"

    def reset(self):
        self.exports = []
        self.regex = []
        self.clips = []
        self.tags = []
        self.filter_text = ""
        self.filter = None
        self.sort_key_text = ""
        self.sort_key = None
        self.dups_only = False
        self.items = []
        self.currentLevel = -1
        self.currentIndex = None
        self.selections = []
        self.clipboard = []
        self.copy_tags = []
        self.workspace = None
        self.storage = None
        self.savedir = None
        self.tempdir = None

        self.horizontalSplitter = False
        self.verticalSplitter = False
        self.tableRowSplitter = False
        self.tableColumnSplitter = False

        self.focusTag = None
        self.bulkMode = False
        self.ocrMode = False
        self.collationMode = False

    def getStorageDir(self, workspace=None):
        if workspace is None:
            workspace = self.workspace
        storage = os.path.join(workspace, ".ctie")
        return storage

    def getLevel(self):
        l = 0
        s = self.clips
        while s:
            l+=1
            ns = []
            for x in s:
                ns.extend(x.children)
            s = ns
        return l

    def setLevel(self, level):
        r = False
        orig = self.getCurrentItem()
        if self.currentLevel != level:
            r = True
            self.currentLevel = level
            self._genItems()
            self.currentIndex = 0
            self.ui.onLevelChanged()
            self.ui.onItemListChanged()
        item = self.getCurrentItem()
        if orig != item:
            self.ui.onItemBlurred(orig)
            self.onItemFocused()
            self.ui.onItemChanged()
        return r

    def selectAllChildren(self):
        item = self.getCurrentItem()
        if item is None:
            return
        self.selections = range(0, len(item.children))
        self.onSelectionChanged()

    def deselectAllChildren(self):
        self.selections = []
        self.onSelectionChanged()

    def selectChildByIndex(self, index):
        item = self.getCurrentItem()
        if item is None:
            return
        if index not in self.selections and index < len(item.children):
            self.selections.append(index)
        self.onSelectionChanged()

    def deselectChildByIndex(self, index):
        if index in self.selections:
            self.selections.remove(index)
        self.onSelectionChanged()

    def onItemFocused(self):
        item = self.getCurrentItem()
        if item:
            self.ui.onItemFocused()
            self.ui.set_status("Item: %d/%d" % (self.getCurrentItemIndex()+1, len(self.items)))
            if self.ocrMode:
                item.ocr()


    def onSelectionChanged(self):
        self.ui.onSelectionChanged()
        item = self.getCurrentItem()
        if item:
            if len(self.selections) == 1:
                child = item.children[self.selections[0]]
                bounds = " ({:.2f},{:.2f},{:.2f},{:.2f})".format(child.x1, child.y1, child.x2, child.y2)
            else:
                bounds = ""
            self.ui.set_status('Area: {} Select: {}{}'.format(len(item.children), ', '.join([str(i+1) for i in self.selections]), bounds))

    def selectItemByIndex(self, index):
        orig = self.getCurrentItem()
        self.currentIndex = index
        item = self.getCurrentItem()
        if orig != item:
            self.selections = []
            self.ui.onItemBlurred(orig)
            self.onItemFocused()
        self.selections = []
        self.ui.onItemChanged()

    def selectNextItem(self):
        orig = self.getCurrentItem()
        if not orig:
            return
        self.currentIndex = (self.currentIndex + 1) % len(self.items)
        item = self.getCurrentItem()
        if orig != item:
            self.selections = []
            self.ui.onItemBlurred(orig)
            self.onItemFocused()
        self.ui.onItemChanged()

    def selectPrevItem(self):
        orig = self.getCurrentItem()
        if not orig:
            return
        self.currentIndex = (self.currentIndex + len(self.items) - 1) % len(self.items)
        item = self.getCurrentItem()
        if orig != item:
            self.selections = []
            self.ui.onItemBlurred(orig)
            self.onItemFocused()
        self.ui.onItemChanged()

    def getCurrentItem(self):
        if self.currentIndex is None:
            return None
        l = self.items[self.currentIndex:]
        if l:
            return l[0]
        return None

    def getCurrentItemIndex(self):
        return self.currentIndex

    def _genItems(self):
        if self.bulkMode:
            return
        self.selections = []
        s = self.clips
        for i in range(0, self.currentLevel):
            ns = []
            for x in s:
                ns.extend(x.children)
            s = ns
        items = []
        for p in s:
            if self.filter and not self.filter.eval(p):
                continue
            items.append(p)
        if self.sort_key:
            sk = []
            for i in items:
                sk.append(self.sort_key.eval(i))
            items = list(zip(items, sk))
            items.sort(key=lambda x:x[1])
            if self.dups_only:
                items = [i for i,k in items if sk.count(k) > 1]
                for i in items:
                    i.flags.add("DUP")
            else:
                items = [x[0] for x in items]
        self.items = items
        self.ui.set_status("{} items".format(len(self.items)))

    def addItemByPath(self, path):
        if os.path.isdir(path):
            cs = os.listdir(path)
            cs.sort(natcmp)
            for c in cs:
                self.addItemByPath(os.path.join(path,c))
        else:
            path = os.path.relpath(path, self.workspace)
            print("Add item from", path)
            if PdfItem.probe(path):
                PdfItem.addItem(self, path)
            elif ImageItem.probe(path):
                ImageItem.addItem(self, path)
        self._genItems()
        self.ui.onItemListChanged()
        self.ui.onItemTreeChanged()
        if self.getCurrentItemIndex() is None:
            self.selectItemByIndex(0)

    def removeItem(self, item):
        focusedItem = self.getCurrentItem()
        if item.parent == focusedItem:
            index = focusedItem.children.index(item)
            if index in self.selections:
                self.selections.remove(index)
        if item in self.clips:
            self.clips.remove(item)
        if item in self.items:
            self.items.remove(item)
        self.ui.onItemListChanged()
        self.ui.onItemTreeChanged()
        self.onItemFocused()
        self.ui.onItemChanged()

    def updateExports(self, exports):
        self.exports = list(exports)
        with open(self.exports_path, 'wb') as fp:
            pickle.dump(self.exports, fp)
        print("Save exports to {}".format(self.exports_path))

    def updateRegex(self, regex, tests):
        self.regex = list(regex)
        self.tests = list(tests)
        with open(self.regex_path, 'wb') as fp:
            pickle.dump({"regex": self.regex, "tests":self.tests}, fp)
        print("Save regex to {}".format(self.regex_path))

    def getRegex(self):
        l = []
        for r in self.regex:
            l.append("\t".join(r))
        return "\n".join(l)

    def setRegex(self, text):
        self.regex = []
        for line in text.split("\n"):
            try:
                a,b = line.split("\t")
                self.regex.append((a, b))
            except:
                pass

    def evalRegex(self, text):
        for pattern, replacement in self.regex:
            text2 = re.sub(pattern, replacement, text)
            text = text2
        return text

    def setItemsSettings(self, filter, sort_key, dups_only, notify=True):
        f = CQL(filter)
        s = CQL(sort_key)

        ok_filter = False
        if f or filter=="":
            self.filter_text = filter
            self.filter = f
            ok_filter = True

        ok_sort = False
        if s or sort_key=="":
            self.sort_key_text = sort_key
            self.sort_key = s
            ok_sort = True

        if ok_filter and ok_sort:
            self.dups_only = dups_only
            if notify:
                self._genItems()
                self.currentIndex = 0
                self.ui.onItemListChanged()
                self.onItemFocused()
                self.ui.onItemChanged()
        else:
            failed = []
            if not ok_filter:
                failed.append("filter")
            if not ok_sort:
                failed.append("sort")
            self.ui.set_status('Failed parsing '+"/".join(failed))

    def load(self, workspace, savepoint):
        self.workspace = workspace

        self.storage = self.getStorageDir()
        if not os.path.exists(self.storage):
            os.makedirs(self.storage)

        self.savedir = os.path.join(self.storage, "save")
        if not os.path.exists(self.savedir):
            os.makedirs(self.savedir)

        self.regex_path = os.path.join(self.storage, "regex")
        self.exports_path = os.path.join(self.storage, "export")

        self.tempdir = os.path.join(self.storage, "tmp")
        if not os.path.exists(self.tempdir):
            os.makedirs(self.tempdir)

        try:
            with open(self.getRegexPath(),'rb') as fp:
                data = pickle.load(fp)
                self.regex = data["regex"]
                self.tests = data["tests"]
        except:
            self.regex = []
            self.tests = []

        try:
            with open(self.exports_path,'rb') as fp:
                self.exports = pickle.load(fp)
        except:
            self.exports = []

        print("Open workspace at {}".format(self.workspace))
        self.ui.onProjectChanged()

        if savepoint:
            savepoint = os.path.join(self.savedir, savepoint)
            print("Load from {}".format(savepoint))
            fp = open(savepoint,'rb')
            try:
                data = pickle.load(fp)
            except:
                return False
            finally:
                fp.close()

            self.clips = data['clips']
            self.tags = data['tags']
            self.copy_tags = data['tags']
            self.currentLevel = data.get("currentLevel", 0)
            self.currentIndex = data.get("currentIndex", 0)
            self.setItemsSettings(data.get("filter", ""), data.get("sort_key", ""), data.get("dups_only", False), notify=False)
            self._genItems()
            self.worker.reset()
            self.worker.addBgJobs(self.clips)

        self.ui.onItemListChanged()
        self.ui.onItemTreeChanged()
        self.ui.onItemChanged()
        self.ui.zoomFit()
        return True

    def save(self, path, confirm=False):
        path = os.path.join(self.savedir, path)
        if os.path.exists(path) and not confirm:
            self.ui.onSaveOverwriteConfirm(path)
            return
        data = {
            'clips':self.clips,
            'tags':self.tags,
            'copy_tags':self.copy_tags,
            'currentLevel':self.currentLevel,
            'currentIndex':self.currentIndex,
            'filter': self.filter_text,
            'sort_key': self.sort_key_text,
            'dups_only': self.dups_only,
        }
        fp = open(path, 'wb')
        pickle.dump(data, fp)
        fp.close()
        print("Save to {}".format(path))

    def list_export(self, outputdir, content, handler, cbProgress):
        content = CQL(content)
        total = len(self.items)
        done = 0
        cbProgress(done, total, False)
        with open(os.path.join(outputdir, "index.html"), "w") as f:
            f.write('<!doctype html><html><head><meta charset="UTF-8"/><style type="text/css">table{border-collapse: collapse;} td {border: solid 1px gray; white-space: pre; font-family: monospace;}</style></head><body><table>')
            cbProgress(done, total, False)
            idx = 0
            for i in self.items:
                idx += 1
                f.write("<tr>")
                f.write("<td>{}</td>".format(idx))
                row = content.eval(i)
                for c in row:
                    f.write("<td>")
                    if hasattr(c, "save"):
                        os.makedirs(os.path.join(outputdir, "data"), exist_ok=True)
                        path = c.save(os.path.join(outputdir, "data", str(idx)))
                        prefix, ext = os.path.splitext(path)
                        extl = ext[1:].lower()
                        if extl in ("jpg","jpeg","ppm","png","gif"):
                            path = utils.image_fallback(path, ("jpg","jpeg","png","gif"), "png")
                            fn = os.path.basename(path)
                            f.write('<img src="{}" alt="{}" />'.format(html.escape(os.path.join("data", fn)), html.escape(fn)))
                        else:
                            fn = os.path.basename(path)
                            f.write('<a href="{}" target="_blank">{}</a>'.format(html.escape(os.path.join("data", os.path.basename(path))), html.escape(fn)))
                    else:
                        f.write(html.escape(str(c)))
                    f.write("</td>")
                f.write("</tr>")
                if handler.isCanceled():
                    cbProgress(done, total, True)
                    break
                done += 1
                cbProgress(done, total, False)
            f.write("</table></body></html>")
        cbProgress(done, total, True)

    def export(self, filter, outputdir, filename, content, overwrite, handler, cbProgress):
        filter = CQL(filter)
        filename = CQL(filename)
        content = CQL(content)
        done = 0
        total = 0
        exported = 0
        todo = self.clips
        while todo:
            newtodo = []
            for item in todo:
                item.resetCache()
                total += 1
                newtodo.extend(item.children)
            todo = newtodo

        cbProgress(done, total, exported, False)
        todo = self.clips
        while todo and not handler.isCanceled():
            newtodo = []
            for item in todo:
                if filter.eval(item):
                    t = item
                    tags = {}
                    while t:
                        for key in t.tags:
                            if key not in tags:
                                tags[key] = t.tags[key]
                        t = t.parent
                    for key in self.tags:
                        if key not in tags:
                            tags[key] = ""

                    path = filename.eval(item)
                    path = os.path.join(outputdir, path)
                    pdir = os.path.dirname(path)
                    if not os.path.exists(pdir):
                        os.makedirs(pdir)
                    if os.path.exists(path):
                        print("Exists:", path)
                        if not overwrite:
                            continue
                    cnt = content.eval(item)
                    if hasattr(cnt, "save"):
                        ok = cnt.save(path)
                    else:
                        f = open(path+".txt",'w')
                        f.write(cnt)
                        f.close()
                        ok = True
                    if ok:
                        exported += 1
                newtodo.extend(item.children)
                done += 1
                cbProgress(done, total, exported, handler.isCanceled())
                if handler.isCanceled():
                    break
            todo = newtodo
        cbProgress(done, total, exported, True)

    def copy(self):
        if not self.selections:
            self.ui.set_status('Nothing to copy, select something!')
        item = self.getCurrentItem()
        if item is None:
            return
        self.clipboard = []
        for i in self.selections:
            child = item.children[i]
            tags = {}
            for key in self.copy_tags:
                if key in child.tags:
                    tags[key] = child.tags[key]
            self.clipboard.append({'x1':child.x1-item.x1, 'y1':child.y1-item.y1, 'x2':child.x2-item.x1 ,'y2':child.y2-item.y1 ,'tags':tags})

    def paste(self):
        if not self.clipboard:
            return
        item = self.getCurrentItem()
        if item is None:
            return
        self.selections = []
        cs = []
        for child in item.children:
            cs.append((child.x1-item.x1, child.y1-item.y1, child.x2-item.x1, child.y2-item.y1))
        for p in self.clipboard:
            x1 = p['x1']
            y1 = p['y1']
            x2 = p['x2']
            y2 = p['y2']
            x1 = max(x1, 0)
            y1 = max(y1, 0)
            x2 = min(x2, item.x2-item.x1)
            y2 = min(y2, item.y2-item.y1)
            if x2-x1>1 and y2-y1>1:
                self.selections.append(len(item.children))
                if (x1,y1,x2,y2) in cs:
                    continue
                item.addChild(x1 = x1+item.x1, y1 = y1+item.y1, x2 = x2+item.x1, y2 = y2+item.y1, tags = p['tags'])
        self.ui.onContentChanged()

    def batchPaste(self, chk_empty, chk_overlap, chk_overlap_aon, chk_boundary, chk_boundary_aon):
        if not self.clipboard:
            return
        item = self.getCurrentItem()
        if item is None:
            return
        total = len(self.items)
        done = 0
        for item in self.items:
            item.batchPaste(self.clipboard, chk_empty, chk_overlap, chk_overlap_aon, chk_boundary, chk_boundary_aon)
            done += 1
            print("{}/{}".format(done, total))
        self.ui.onContentChanged()

    def autoPaste(self):
        if not self.clipboard:
            return
        item = self.getCurrentItem()
        if item is None:
            return
        for item in self.items:
            if item.children:
                continue
            item.autoPaste(self.clipboard)
        self.ui.onContentChanged()

    def deleteSelectedChildren(self):
        item = self.getCurrentItem()
        if item is None:
            return
        self.selections.sort()
        self.selections.reverse()
        for i in self.selections:
            del(item.children[i])
        self.selections = []
        self.ui.onItemTreeChanged()
        self.ui.onContentChanged()

    def updateCopyTags(self, tags):
        self.copy_tags = tags

    def enableCopyTag(self, key):
        if key in self.tags and key not in self.copy_tags:
            self.copy_tags.append(key)

    def disableCopyTag(self, key):
        if key in self.copy_tags:
            self.copy_tags.remove(key)

    def addTag(self, key, byUser=False):
        if key.startswith("_"):
            return
        if not key in self.tags:
            self.tags.append(key)
        else:
            if byUser:
                self.ui.set_status('Tag "{}" already exists'.format(key))
        self.ui.onTagChanged()

    def getTags(self, item = None):
        if item is None:
            return self.tags
        tags = item.getTags()
        for tag in self.tags:
            if tag not in tags:
                tags[tag] = ""
        return tags

    def selectPrevChild(self):
        item = self.getCurrentItem()
        if item is None:
            return
        if not item.children:
            pass
        elif len(self.selections)!=1:
            self.selections = [0]
        else:
            self.selections[0] += len(item.children)-1
            self.selections[0] %= len(item.children)
        self.onSelectionChanged()

    def selectNextChild(self):
        item = self.getCurrentItem()
        if item is None:
            return
        if not item.children:
            pass
        elif len(self.selections)!=1:
            self.selections = [0]
        else:
            self.selections[0] += 1
            self.selections[0] %= len(item.children)
        self.onSelectionChanged()

    def move(self, xoff, yoff):
        item = self.getCurrentItem()
        if item is None:
            return
        for i in self.selections:
            item.move(i, xoff, yoff)

    def resize(self, xoff, yoff):
        item = self.getCurrentItem()
        if item is None:
            return
        selections = list(self.selections)
        selections.sort(reverse = True)
        for i in selections:
            item.resize(i, xoff, yoff)

    def reorder_children(self):
        item = self.getCurrentItem()
        if item is None:
            return
        item.reorder_children(self.selections)
        self.selections = range(0,len(item.children))
        self.onSelectionChanged()

    def batchSetTag(self, key, value, isFormula, cbProgress):
        self.ui.core.worker.addFgJob(functools.partial(self._batchSetTag, key, value, isFormula, cbProgress))

    def _batchSetTag(self, key, value, isFormula, cbProgress):
        if not key.startswith("_") and key not in self.tags:
            self.tags.append(key)
        done = 0
        total = len(self.items)
        cbProgress(done, total)
        for it in self.items:
            it.setTag(key, value, isFormula)
            done += 1
            cbProgress(done, total)
        self.ui.onTagChanged()

    def batchTrim(self, left, top, right, bottom, margin, cbProgress):
        self.ui.core.worker.addFgJob(functools.partial(self._batchTrim, left, top, right, bottom, margin, cbProgress))

    def _batchTrim(self, left, top, right, bottom, margin, cbProgress):
        done = 0
        total = len(self.items)
        cbProgress(done, total)
        for item in self.items:
            item.trim(left, top, right, bottom, margin)
            done += 1
            cbProgress(done, total)
        self.edge_limiter(self.items)
        self.ui.onContentChanged()
        self.ui.onItemChanged()
        self.ui.onItemListChanged()

    def batchShrink(self, left, top, right, bottom, amount, cbProgress):
        self.ui.core.worker.addFgJob(functools.partial(self._batchShrink, left, top, right, bottom, amount, cbProgress))

    def _batchShrink(self, left, top, right, bottom, amount, cbProgress):
        done = 0
        total = len(self.items)
        cbProgress(done, total)
        for item in self.items:
            item.shrink(left, top, right, bottom, amount)
            done += 1
            cbProgress(done, total)
        self.edge_limiter(self.items)
        self.ui.onContentChanged()
        self.ui.onItemChanged()
        self.ui.onItemListChanged()

    def batchDetectTableSeparator(self, detectRowSep, minRowSep, detectColSep, minColSep, cbProgress):
        self.ui.core.worker.addFgJob(functools.partial(self._batchDetectTableSeparator, detectRowSep, minRowSep, detectColSep, minColSep, cbProgress))

    def _batchDetectTableSeparator(self, detectRowSep, minRowSep, detectColSep, minColSep, cbProgress):
        done = 0
        total = len(self.items)
        cbProgress(done, total)
        for item in self.items:
            item.detectTableSeparator(detectRowSep, minRowSep, detectColSep, minColSep)
            done += 1
            cbProgress(done, total)
        self.ui.onContentChanged()

    def batchColsToChildren(self, cbProgress):
        self.ui.core.worker.addFgJob(functools.partial(self._batchColsToChildren, cbProgress))

    def _batchColsToChildren(self, cbProgress):
        done = 0
        total = len(self.items)
        cbProgress(done, total)
        for item in self.items:
            item.colsToChildren()
            done += 1
            cbProgress(done, total)
        self.ui.onContentChanged()
        self.ui.onItemChanged()
        self.ui.onItemListChanged()

    def batchRowsToChildren(self, cbProgress):
        self.ui.core.worker.addFgJob(functools.partial(self._batchRowsToChildren, cbProgress))

    def _batchRowsToChildren(self, cbProgress):
        done = 0
        total = len(self.items)
        cbProgress(done, total)
        for item in self.items:
            item.rowsToChildren()
            done += 1
            cbProgress(done, total)
        self.ui.onContentChanged()
        self.ui.onItemChanged()
        self.ui.onItemListChanged()

    def batchDenoise(self, min_width, min_height, cbProgress):
        self.ui.core.worker.addFgJob(functools.partial(self._batchDenoise, min_width, min_height, cbProgress))

    def _batchDenoise(self, min_width, min_height, cbProgress):
        done = 0
        total = len(self.items)
        cbProgress(done, total)
        for item in self.items:
            item.denoise(min_width, min_height)
            done += 1
            cbProgress(done, total)
        self.ui.onContentChanged()
        self.ui.onItemChanged()
        self.ui.onItemListChanged()

    def edge_limiter(self, todo):
        while todo:
            delete = []
            newtodo = []
            for item in todo:
                x1 = item.x1
                y1 = item.y1
                x = item.x2
                y = item.y2
                if x1>x:
                    x1,x = x,x1
                if y1>y:
                    y1,y = y,y1
                if item.parent:
                    item.x1 = max(x1, item.parent.x1)
                    item.y1 = max(y1, item.parent.y1)
                    item.x2 = min(x, item.parent.x2)
                    item.y2 = min(y, item.parent.y2)
                if abs(x-x1)<=1 or abs(y-y1)<=1:
                    delete.append(item)
                else:
                    newtodo.extend(item.children)
            todo = newtodo
            for item in delete:
                if item.parent:
                    item.parent.children.remove(item)
                else:
                    self.clips.remove(item)

    def setHorizontalSplitter(self, enable):
        self.horizontalSplitter = enable
        if enable:
            self.ui.setTableRowSplitter(False)
            self.ui.setTableColumnSplitter(False)

    def setVerticalSplitter(self, enable):
        self.verticalSplitter = enable
        if enable:
            self.ui.setTableRowSplitter(False)
            self.ui.setTableColumnSplitter(False)

    def setTableRowSplitter(self, enable):
        self.tableRowSplitter = enable
        if enable:
            self.ui.setHorizontalSplitter(False)
            self.ui.setVerticalSplitter(False)

    def setTableColumnSplitter(self, enable):
        self.tableColumnSplitter = enable
        if enable:
            self.ui.setHorizontalSplitter(False)
            self.ui.setVerticalSplitter(False)

    def setOcrMode(self, enabled):
        self.ocrMode = enabled
        print("OcrMode:", enabled)
        if enabled:
            self.onItemFocused()

    def setCollationMode(self, enabled):
        self.collationMode = enabled
        print("CollationMode:", enabled)
        self.onSetCollationMode()

    def onSetCollationMode(self):
        self.ui.onSetCollationMode()

    def setFocusTag(self, tag):
        self.focusTag = tag
        self.ui.onSetFocusTag()