from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from functools import partial
from .QTagEdit import *

class TagManager():
    ITEM = 1
    CHILD = 2

    def __init__(self, ui, edit_new_tag, btn_new_tag, panel_child_tags, item_tags, child_tags):
        self.ui = ui
        self.edit_new_tag = edit_new_tag
        self.btn_new_tag = btn_new_tag
        self.panel_child_tags = panel_child_tags
        self.item_tags = item_tags
        self.child_tags = child_tags
        self.hasFocus = 0
        self.item = None
        self.blockItemUpdated = False
        self.blockFocus = False
        btn_new_tag.clicked.connect(self.add_tag)

    def onItemChanged(self):
        self.refresh_tags()

    def onTagChanged(self):
        self.refresh_tags()

    def onSelectionChanged(self):
        self.refresh_tags()

    def refresh_tags(self):
        self.blockFocus = True
        tbd = []
        for r in range(self.item_tags.rowCount()):
            for c in range(self.item_tags.columnCount()):
                item = self.item_tags.itemAtPosition(r, c)
                if item:
                    widget = item.widget()
                    if widget:
                        tbd.append(widget)
        for widget in tbd:
            widget.setParent(None)
            widget.deleteLater()

        tbd = []
        for r in range(self.child_tags.rowCount()):
            for c in range(self.child_tags.columnCount()):
                item = self.child_tags.itemAtPosition(r, c)
                if item:
                    widget = item.widget()
                    if widget:
                        tbd.append(widget)
        for widget in tbd:
            widget.setParent(None)
            widget.deleteLater()

        if self.item:
            self.item.removeListener(self.onItemUpdated)
            self.item = None

        item = self.ui.core.getCurrentItem()
        self.blockFocus = False
        if item is None:
            return

        self.item = item
        self.item.addListener(self.onItemUpdated)

        r = 0
        for tag in self.ui.core.getTags():
            label = QLabel()
            label.setText(tag)

            edit = QTagEdit()
            edit.setPlainText(item.getTag(tag))
            edit.setPlaceholderText(item.getTagFromParent(tag))
            edit.textChanged.connect(partial(self.set_tag, item, tag, edit))

            self.item_tags.addWidget(label, r, 0)
            self.item_tags.addWidget(edit, r, 1)

            if self.hasFocus==self.ITEM and self.ui.core.focusTag == tag:
                edit.setFocus()
            edit.focusIn.connect(partial(self.focusIn, self.ITEM, tag))
            edit.focusOut.connect(self.focusOut)
            r += 1

        if len(self.ui.core.selections)==1:
            self.panel_child_tags.setVisible(True)

            child = item.children[self.ui.core.selections[0]]

            r = 0
            for tag in self.ui.core.getTags():
                label = QLabel()
                label.setText(tag)

                edit = QTagEdit()
                edit.setPlainText(child.getTag(tag))
                edit.setPlaceholderText(child.getTagFromParent(tag))
                edit.textChanged.connect(partial(self.set_tag, child, tag, edit))

                self.child_tags.addWidget(label, r, 0)
                self.child_tags.addWidget(edit, r, 1)

                if self.hasFocus==self.CHILD and self.ui.core.focusTag == tag:
                    edit.setFocus()
                edit.focusIn.connect(partial(self.focusIn, self.CHILD, tag))
                edit.focusOut.connect(self.focusOut)

                r += 1
        else:
            self.panel_child_tags.setVisible(False)

    def set_tag(self, item, tag, edit):
        value = edit.toPlainText()
        self.blockItemUpdated = True
        item.setTag(tag, value)
        self.blockItemUpdated = False

    def add_tag(self):
        tag = self.edit_new_tag.text()
        self.ui.core.addTag(tag, byUser=True)

    def focusIn(self, type, tag):
        self.hasFocus = type
        self.ui.core.setFocusTag(tag)

    def focusOut(self):
        if self.blockFocus:
            return
        self.hasFocus = 0

    def onItemUpdated(self):
        if self.blockItemUpdated:
            return
        self.refresh_tags()