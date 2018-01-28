from PySide import QtGui, QtCore
from functools import partial

class TagManager():
    def __init__(self, ui, edit_new_tag, btn_new_tag, panel_child_tags, item_tags, child_tags):
        self.ui = ui
        self.edit_new_tag = edit_new_tag
        self.btn_new_tag = btn_new_tag
        self.panel_child_tags = panel_child_tags
        self.item_tags = item_tags
        self.child_tags = child_tags
        btn_new_tag.clicked.connect(self.add_tag)

    def onItemChanged(self):
        self.refresh_tags()

    def onTagChanged(self):
        self.refresh_tags()

    def refresh_tags(self):
        for r in range(self.item_tags.rowCount()):
            for c in range(self.item_tags.columnCount()):
                item = self.item_tags.itemAtPosition(r, c)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()

        for r in range(self.child_tags.rowCount()):
            for c in range(self.child_tags.columnCount()):
                item = self.child_tags.itemAtPosition(r, c)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()

        item = self.ui.core.getCurrentItem()
        if item is None:
            return

        r = 0
        for tag in self.ui.core.getTags():
            label = QtGui.QLabel()
            label.setText(tag)

            edit = QtGui.QLineEdit()
            edit.textChanged.connect(partial(self.set_tag, item, tag))

            self.item_tags.addWidget(label, r, 0)
            self.item_tags.addWidget(edit, r, 1)
            r += 1

    def set_tag(self, item, tag, value):
        item.setTag(tag, value)

    def add_tag(self):
        tag = self.edit_new_tag.text()
        self.ui.core.addTag(tag)
