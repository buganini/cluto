import os
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic, QtCore
from helpers import *
from .keyBinding import *
from .loadDialog import *
from .saveDialog import *
from .regexManager import *
from .menubar import *
from .toolbar import *
from .itemList import *
from .levelSelector import *
from .collationView import *
from .workArea import *
from .tagManager import *
from .helper import *

# http://www.noobslab.com/2014/03/give-new-looks-to-gimp-image-editor.html

clear_tempdir = True

class MainUI():
    def __init__(self, klass, argv):
        self.core = klass(self)
        self.uiref = {}
        self.app_path = os.path.abspath(os.path.dirname(__file__))

        uiFile = "main.ui"

        app = QApplication(sys.argv)
        ui = uic.loadUi(os.path.join(self.app_path, uiFile))
        ui.show()
        self.ui = ui
        self.uiref["main"] = ui

        self.key_binding = KeyBinding(self)

        #toolbar
        self.uiMenuBar = Menubar(self, ui.findChild(QMenuBar, "menubar"))
        self.uiToolBar = Toolbar(self, ui.findChild(QToolBar, "toolBar"))
        self.uiMainSplitter = ui.findChild(QSplitter, "main_splitter")
        self.uiMainSplitter.setSizes([360, 1, 320])
        self.uiMainSplitter.setStretchFactor(1, 1)
        self.uiItemList = ItemList(self, ui.findChild(QVBoxLayout, "itemList"), ui.findChild(QScrollArea, "itemListScroller"), ui.findChild(QVBoxLayout, "items_settings"), ui.findChild(QPushButton, "btn_apply"))
        self.uiStatusBar = ui.findChild(QStatusBar, "statusBar")
        self.uiWorkArea = WorkArea(self, ui.findChild(QScrollArea, "workAreaScroller"))

        uiCollcationSplitter = ui.findChild(QSplitter, "collationSplitter")
        uiCollcationSplitter.setStretchFactor(0, 1)
        uiCollcationSplitter.setStretchFactor(1, 0)
        self.uiCollationView = CollationView(self, uiCollcationSplitter, ui.findChild(QVBoxLayout, "collationView"), ui.findChild(QScrollArea, "collationViewAreaScroller"))

        self.uiLevelSelector = LevelSelector(self, ui.findChild(QComboBox, "level"))
        self.uiTagManager = TagManager(
            self,
            ui.findChild(QLineEdit, "edit_new_tag"),
            ui.findChild(QPushButton, "btn_new_tag"),
            ui.findChild(QWidget, "panel_child_tags"),
            ui.findChild(QGridLayout, "item_tags"),
            ui.findChild(QGridLayout, "child_tags"),
        )

        self.core.workspace = argv.get("workspace")

        timer = QtCore.QTimer(app)
        timer.singleShot(1, self.load)

        self.onSetCollationMode()

        r = app.exec_()
        self.core.worker.stop()
        sys.exit(r)

    @UI
    def onProjectChanged(self):
        self.uiToolBar.onProjectChanged()
        self.uiItemList.onProjectChanged()
        self.uiLevelSelector.onProjectChanged()
        self.uiWorkArea.onProjectChanged()
        self.uiTagManager.onProjectChanged()
        self.uiCollationView.onProjectChanged()

    @UI
    def onLevelChanged(self):
        self.uiItemList.onLevelChanged()

    @UI
    def set_status(self, s):
        self.uiStatusBar.showMessage(s)

    def selectPreviousItem(self, *arg):
        item = self.core.getCurrentItem()
        if item is None:
            return
        self.core.selectPrevItem()

    def selectNextItem(self, *arg):
        item = self.core.getCurrentItem()
        if item is None:
            return
        self.core.selectNextItem()

    def key_press(self, obj, evt):
        collation_mode = self.toggle_collation.get_active()
        if evt.keyval==Gdk.KEY_Page_Down:
            if not collation_mode or evt.state & Gdk.ModifierType.CONTROL_MASK:
                self.selectNextItem()
            else:
                self.core.selectNextChild()
        elif evt.keyval==Gdk.KEY_Page_Up:
            if not collation_mode or evt.state & Gdk.ModifierType.CONTROL_MASK:
                self.selectPreviousItem()
            else:
                self.core.selectPrevChild()
        elif evt.keyval==Gdk.KEY_Delete and self.canvas.has_focus():
            self.delete()
        elif (evt.keyval==Gdk.KEY_A or evt.keyval==Gdk.KEY_a) and evt.state & Gdk.ModifierType.CONTROL_MASK and self.canvas.has_focus():
            self.core.deselectAllChildren()
            if not evt.state & Gdk.ModifierType.SHIFT_MASK:
                self.core.selectAllChildren()
        elif (evt.keyval==Gdk.KEY_C or evt.keyval==Gdk.KEY_c) and evt.state & Gdk.ModifierType.CONTROL_MASK and self.canvas.has_focus():
            self.copy()
        elif (evt.keyval==Gdk.KEY_V or evt.keyval==Gdk.KEY_v) and evt.state & Gdk.ModifierType.CONTROL_MASK and self.canvas.has_focus():
            self.paste()

    def load(self):
        LoadDialog(self)

    def save(self):
        SaveDialog(self)

    def onSaveOverwriteConfirm(self, path):
        ret = QMessageBox.question(self.ui, 'Save', "Target already exists, overwrite?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.core.save(path, True)

    def copy_setting_toggle(self, obj, key):
        if obj.get_active():
            self.core.enableCopyTag(key)
        else:
            self.core.disableCopyTag(key)

    def delete(self, *arg):
        self.core.deleteSelectedChildren()

    def zoomFit(self, *arg):
        self.uiWorkArea.zoomFit()

    def zoomActual(self, *arg):
        self.uiWorkArea.zoomActual()

    def remove_item(self, *arg):
        item = self.core.getCurrentItem()
        if item is None:
            return
        item.remove()

    def set_children_order(self, *arg):
        if not self.toggle_childrenpath:
            self.set_status("Please enable areas path display")
            return
        self.core.reorder_children()

    def set_type(self, obj, data):
        item, t = data
        if obj.get_active():
            item.setType(t)

    def autofocus(self, *arg):
        if self.focus_entry:
            if not self.focus_entry.get_text():
                auto_fill = self.builder.get_object("auto_fill").get_active_text()
                if auto_fill=="Clipboard":
                    self.focus_entry.paste_clipboard()
                    GObject.idle_add(self.autofocus2)
                self.focus_entry.grab_focus()
            else:
                self.focus_entry.grab_focus()
                self.focus_entry = None

    def autofocus2(self, *arg):
        if not self.focus_entry:
            return
        self.focus_entry.set_position(-1)
        self.focus_entry = None

    def entry_focus(self, obj, evt, data, *arg):
        t,item,tag = data
        self.focus_field = (t,tag)
        self.collation_cb(obj)

    def set_tag(self, obj, data):
        item, key = data
        item.setTag(key, obj.get_buffer().get_text())
        self.collation_cb(obj)

    def collation_cb(self, obj, *arg):
        if self.toggle_collation.get_active() and self.focus_field and self.focus_field[0]=='c':
            self.builder.get_object("editor_label").set_text(self.focus_field[1])
            self.builder.get_object("collation_window").show()
            self.builder.get_object("collation_editor").master = obj
            if not self.signal_mask and obj:
                GObject.idle_add(self.focus_collation_editor)
                self.signal_mask = True
                self.builder.get_object("collation_editor").set_text(obj.get_text())
                self.signal_mask = False
        else:
            self.builder.get_object("collation_window").hide()

    def focus_collation_editor(self):
        self.builder.get_object("collation_editor").grab_focus()
        GObject.idle_add(self.focus_collation_editor2)

    def focus_collation_editor2(self, *arg):
        self.builder.get_object("collation_editor").set_position(0)

    def collation_editor_changed(self, obj, *arg):
        master = obj.master
        if master and not self.signal_mask:
            self.signal_mask = True
            master.set_text(obj.get_text())
            self.signal_mask = False

    def clear_tag(self, obj, data):
        item, key = data

    @UI
    def onItemListChanged(self):
        self.uiItemList.onItemListChanged()

    @UI
    def onItemChanged(self):
        self.uiWorkArea.onItemChanged()
        self.uiCollationView.onItemChanged()
        self.uiTagManager.onItemChanged()
        self.uiToolBar.onItemChanged()

    @UI
    def onSelectionChanged(self):
        self.uiTagManager.onSelectionChanged()
        self.uiWorkArea.onSelectionChanged()
        self.uiCollationView.onSelectionChanged()

    @UI
    def onItemTreeChanged(self):
        self.uiLevelSelector.onItemTreeChanged()
        self.uiItemList.onItemTreeChanged()
        if self.core.bulkMode:
            return

    @UI
    def onContentChanged(self):
        self.uiWorkArea.onContentChanged()
        self.uiCollationView.onContentChanged()
        self.uiToolBar.onContentChanged()

    @UI
    def onTagChanged(self):
        self.uiTagManager.onTagChanged()

    @UI
    def onItemFocused(self):
        item = self.core.getCurrentItem()
        if not item:
            return
        self.uiItemList.onItemFocused(item)

    @UI
    def onItemBlurred(self, item):
        if not item:
            return
        self.uiItemList.onItemBlurred(item)

    @UI
    def onSetCollationMode(self):
        self.uiCollationView.onSetCollationMode()

    @UI
    def onSetFocusTag(self):
        self.uiCollationView.onSetFocusTag()

    @UI
    def updateToolBar(self):
        self.uiToolBar.updateUI()

    @UI
    def setHorizontalSplitter(self, enable):
        self.uiToolBar.setHorizontalSplitter(enable)

    @UI
    def setVerticalSplitter(self, enable):
        self.uiToolBar.setVerticalSplitter(enable)

    @UI
    def setTableRowSplitter(self, enable):
        self.uiToolBar.setTableRowSplitter(enable)

    @UI
    def setTableColumnSplitter(self, enable):
        self.uiToolBar.setTableColumnSplitter(enable)