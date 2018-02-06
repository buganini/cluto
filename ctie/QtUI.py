import os
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic, QtCore
from helpers import *
from ctie import *
from qt import *
import utils

class Clicked(QtCore.QObject):
    def __init__(self, action):
        action.triggered.connect(self.triggered)

    def triggered(self):
        pass

# http://www.noobslab.com/2014/03/give-new-looks-to-gimp-image-editor.html

clear_tempdir = True

class CtieUI():
    def __init__(self):
        self.utils = utils
        self.core = Ctie(self)
        self.signal_mask = False
        self.focus_field = (None, None)
        self.focus_entry = None
        self.preview_canvas = None
        self.canvas = None
        self.zoom = 100
        self.selstart = (None, None)
        self.selend = (None, None)
        self.mode = None
        self.uiref = {}
        self.app_path = os.path.abspath(os.path.dirname(__file__))

        uiFile = "ctie.ui"

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
        self.uiItemList = ItemList(self, ui.findChild(QVBoxLayout, "itemList"), ui.findChild(QScrollArea, "itemListScroller"))
        self.uiStatusBar = ui.findChild(QStatusBar, "statusBar")
        self.uiWorkArea = WorkArea(self, ui.findChild(QScrollArea, "workAreaScroller"))
        self.uiLevelSelector = LevelSelector(self, ui.findChild(QComboBox, "level"))
        self.uiItemFilter = ItemFilter(self, ui.findChild(QLineEdit, "edit_filter"), ui.findChild(QPushButton, "btn_filter"))
        self.uiTagManager = TagManager(
            self,
            ui.findChild(QLineEdit, "edit_new_tag"),
            ui.findChild(QPushButton, "btn_new_tag"),
            ui.findChild(QWidget, "panel_child_tags"),
            ui.findChild(QGridLayout, "item_tags"),
            ui.findChild(QGridLayout, "child_tags"),
        )
        self.uiCollcationSplitter = ui.findChild(QSplitter, "collationSplitter")
        self.uiCollcationSplitter.setSizes([1, 0])
        self.uiCollcationSplitter.handle(1).setEnabled(False)

        timer = QtCore.QTimer(app)
        timer.singleShot(1, self.openProject)

        sys.exit(app.exec_())

    def openProject(self):
        project = QFileDialog.getExistingDirectory(self.ui, u"Select Project Folder")
        if project:
            self.core.openProject(project)

    def onProjectInitConfirm(self, path):
        ret = QMessageBox.question(self.ui, 'New Project', "Selected folder is not a ctie project folder, configure it as a project?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.core.openProject(path, True)

    def onProjectChanged(self):
        self.uiToolBar.onProjectChanged()

    def onLevelChanged(self):
        self.uiItemList.onLevelChanged()

    def set_status(self, s):
        self.uiStatusBar.showMessage(s)

    def zoomActual(self):
        self.uiWorkArea.zoomActual()

    def zoomFit(self):
        self.uiWorkArea.zoomFit()

    def edit_regex(self, *arg):
        self.builder.get_object("regex").get_buffer().set_text(self.core.getRegex())
        self.builder.get_object("regex_window").show()

    def regex_apply(self, *arg):
        b = self.builder.get_object("regex").get_buffer()
        text = b.get_text(b.get_start_iter(), b.get_end_iter(), 0).strip()
        try:
            text = text.decode("utf-8")
        except:
            pass
        self.core.setRegex(text)
        self.builder.get_object("regex_window").hide()

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

    def set_value(self, *arg):
        self.builder.get_object('set_value_window').show()

    def set_value_apply(self, *arg):
        key = self.builder.get_object('set_value_key').get_text()
        value = self.builder.get_object('set_value_value').get_text()
        isFormula = self.builder.get_object('set_value_value_is_formula').get_active()
        if not key:
            return
        self.core.batchSetTag(key, value, isFormula)

    def load(self):
        LoadDialog(self)

    def save(self):
        SaveDialog(self)

    def onSaveOverwriteConfirm(self, path):
        ret = QMessageBox.question(self.ui, 'Save', "Target already exists, overwrite?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.core.save(path, True)

    def copy_setting(self, obj, *arg):
        tagsbox = self.builder.get_object("copy_setting_tags")
        c = tagsbox.get_child()
        if c:
            tagsbox.remove(c)
        tags_table = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        tagsbox.add(tags_table)
        for i,key in enumerate(self.core.tags):
            toggle = Gtk.CheckButton.new_with_label(key)
            if key in self.core.copy_tags:
                toggle.set_active(True)
            else:
                toggle.set_active(False)
            toggle.connect('toggled', self.copy_setting_toggle, key)
            tags_table.pack_start(toggle,False,False,0)
        self.builder.get_object("copy_setting_window").show_all()

    def copy_setting_toggle(self, obj, key):
        if obj.get_active():
            self.core.enableCopyTag(key)
        else:
            self.core.disableCopyTag(key)

    def copy(self, *arg):
        self.core.copy()

    def paste(self, *arg):
        self.core.paste()
        self.canvas.queue_draw()

    def autopaste(self, *arg):
        self.core.autoPaste()
        self.canvas.queue_draw()

    def delete(self, *arg):
        self.core.deleteSelectedChildren()

    def do_export(self, *arg):
        outputdir = self.builder.get_object('output_dir').get_filename()
        export_filter = CQL(self.builder.get_object('export_filter').get_text())
        if not export_filter:
            print("Invalid filter")
            return
        export_content = CQL(self.builder.get_object('export_content').get_text())
        if not export_content:
            print("Invalid content")
            return
        export_path = CQL(self.builder.get_object('path_pattern').get_text())
        if not export_path:
            print("Invalid path")
            return
        self.core.export(export_filter, export_content, export_path, outputdir)

    def append_tag(self, *arg):
        b = self.builder.get_object('path_pattern')
        b.set_text("%s${%s}" % (b.get_text(), self.builder.get_object('tags_list').get_active_text()))

    def export_show(self, *arg):
        self.builder.get_object('export_window').show()

    def add_tag(self, *arg):
        tag = self.builder.get_object('new_tag').get_text()
        if not tag:
            return
        self.core.addTag(tag)

    def preview_draw(self, widget, cr):
        item = self.core.getCurrentItem()
        if item is None:
            return
        if len(self.core.selections)!=1:
            return
        child = item.children[self.core.selections[0]]
        width = child.x2-child.x1
        height = child.y2-child.y1

        self.canvas.set_size_request(width, height)

        child.draw(self.preview_canvas, cr, 1)

    def zoom_fit(self, *arg):
        item = self.core.getCurrentItem()
        if item is None or not self.canvas:
            return
        workarea_window = self.builder.get_object('workarea_window')
        alloc = workarea_window.get_allocation()
        win_width = alloc.width
        win_height = alloc.height
        width = item.x2-item.x1
        height = item.y2-item.y1
        if width>win_width*0.8:
            self.zoom = (win_width*0.8/width)*100
        else:
            self.zoom = 100
        self.canvas.queue_draw()

    def zoom_100(self, *arg):
        if not self.canvas:
            return
        self.zoom = 100
        self.canvas.queue_draw()

    def zoom_in(self, *arg):
        if not self.canvas:
            return
        self.zoom += 5
        self.canvas.queue_draw()

    def zoom_out(self, *arg):
        if not self.canvas:
            return
        if self.zoom>5:
            self.zoom -= 5
        self.canvas.queue_draw()

    def remove_item(self, *arg):
        item = self.core.getCurrentItem()
        if item is None:
            return
        item.remove()

    def add_item(self, *arg):
        filec = Gtk.FileChooserDialog("Add", self.builder.get_object("main_window"), Gtk.FileChooserAction.OPEN | Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_ADD, Gtk.ResponseType.ACCEPT))
        filec.set_select_multiple(True)
        if Gtk.Dialog.run(filec)==Gtk.ResponseType.ACCEPT:
            self.core.bulkMode = True
            cs = filec.get_filenames()
            cs.sort(natcmp)
            for path in cs:
                self.core.addItemByPath(path)
            filec.destroy()
            self.core.bulkMode = False
            self.onItemTreeChanged()
        else:
            filec.destroy()
            return

    def change_level(self, *arg):
        level = self.builder.get_object("level").get_active_text()
        if level is None:
            return
        level = int(level)
        if self.core.setLevel(level):
            self.focus_field = (None, None)

    def redraw_items_list(self, *arg):
        items_list = self.builder.get_object("items_list")
        for c in items_list.get_children():
            items_list.remove(c)
        for idx, item in enumerate(self.core.items):
            if hasattr(item, "ui"):
                evtbox = item.ui
            else:
                evtbox = Gtk.EventBox()
                box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
                label = Gtk.Label(os.path.basename(item.path))
                canvas = Gtk.DrawingArea()
                canvas.connect("draw", item.drawThumbnail)
                canvas.set_size_request(160, 240)
                box.pack_start(canvas, False, False, 0)
                box.pack_start(label, False, False, 0)
                evtbox.add(box)
                evtbox.p = item
                item.ui = evtbox
            evtbox.index = idx
            evtbox.get_style_context().add_provider(self.css, 10)
            evtbox.connect("button-press-event", self.item_button_press)
            items_list.pack_start(evtbox, False, False, 5)
            evtbox.show_all()

    def set_children_order(self, *arg):
        if not self.toggle_childrenpath:
            self.set_status("Please enable areas path display")
            return
        self.core.reorder_children()

    def level_sanitize(self):
        level = self.builder.get_object("level")
        l = self.core.getLevel()
        try:
            active = int(level.get_active_text())
        except:
            active = 0
        level.remove_all()
        for i in range(0,l):
            level.append_text(str(i))
        if active<l:
            level.set_active(active)
            self.core.setLevel(active)
        else:
            level.set_active(l-1)
            self.core.setLevel(l-1)

    def item_button_press(self, obj, evt):
        if evt.button==1 and evt.type==Gdk.EventType.BUTTON_PRESS:
            self.core.selectItemByIndex(obj.index)

    def tags_refresh(self, *arg):
        item = self.core.getCurrentItem()
        if item is None:
            return
        self.builder.get_object('tags_pane').show_all()

        tagsbox = self.builder.get_object('tags')
        c = tagsbox.get_child()
        if c:
            tagsbox.remove(c)
        collation_editor = self.builder.get_object("collation_editor")
        collation_editor.master = None
        collation_editor.set_text("")

        grid_i = 0
        tags_table = Gtk.Grid()
        tagsbox.add(tags_table)

        types = item.getTypes()
        if types:
            group = None
            for t in types:
                radio = Gtk.RadioButton.new_with_label_from_widget(group, t)
                group = radio
                if t == item.getType():
                    radio.set_active(True)
                else:
                    radio.set_active(False)
                radio.connect('toggled', self.set_type, (item, t))
                tags_table.attach(radio,0,grid_i,3,1)
                grid_i += 1

        tags = self.core.getTags(item)
        for tag in self.core.tags:
            text = Gtk.Entry()
            text.set_text(tags[tag])
            text.connect('changed', self.set_tag, (item, tag))
            text.connect("focus-in-event", self.entry_focus, ('p', item, tag))
            if self.focus_field[0]=='p' and self.focus_field[1]==tag:
                self.focus_entry = text
            label = Gtk.Label(tag)
            button = Gtk.Button()
            btn_img = Gtk.Image.new_from_stock(Gtk.STOCK_CLEAR, Gtk.IconSize.BUTTON)
            button.set_image(btn_img)
            button.connect("clicked", self.clear_tag, (item, tag))
            tags_table.attach(label,0,grid_i,1,1)
            tags_table.attach(text,1,grid_i,1,1)
            tags_table.attach(button,2,grid_i,1,1)
            grid_i += 1
        tagsbox.show_all()
        GObject.idle_add(self.autofocus)
        self.child_tags_refresh()

    def set_type(self, obj, data):
        item, t = data
        if obj.get_active():
            item.setType(t)

    def child_tags_refresh(self, *arg):
        item = self.core.getCurrentItem()
        if item is None:
            return

        tagsbox = self.builder.get_object('child_tags')
        c = tagsbox.get_child()
        if c:
            tagsbox.remove(c)

        if len(self.core.selections)!=1:
            return

        child = item.children[self.core.selections[0]]
        tags = self.core.getTags(child)

        grid_i = 0
        tags_table = Gtk.Grid()
        tagsbox.add(tags_table)

        types = child.getTypes()
        if types:
            group = None
            for t in types:
                radio = Gtk.RadioButton.new_with_label_from_widget(group, t)
                group = radio
                if t == child.getType():
                    radio.set_active(True)
                else:
                    radio.set_active(False)
                radio.connect('toggled', self.set_type, (child, t))
                tags_table.attach(radio,0,grid_i,3,1)
                grid_i += 1

        for key in self.core.tags:
            text = Gtk.Entry()
            text.set_text(tags[key])
            text.connect('changed', self.set_tag, (child, key))
            text.connect("focus-in-event", self.entry_focus, ('c', child, key))

            if self.focus_field[0]=='c' and self.focus_field[1]==key:
                self.focus_entry = text
            label = Gtk.Label(key)
            button = Gtk.Button()
            btn_img = Gtk.Image.new_from_stock(Gtk.STOCK_CLEAR, Gtk.IconSize.BUTTON)
            button.set_image(btn_img)
            button.connect("clicked", self.clear_tag, (child, key))
            tags_table.attach(label,0,grid_i,1,1)
            tags_table.attach(text,1,grid_i,1,1)
            tags_table.attach(button,2,grid_i,1,1)
            grid_i += 1
        tagsbox.show_all()
        self.collation_cb(None)
        GObject.idle_add(self.autofocus)

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

    def onItemListChanged(self):
        self.uiItemList.onItemListChanged()

    def onItemChanged(self):
        self.uiWorkArea.onItemChanged()
        self.uiTagManager.onItemChanged()
        # self.preview_canvas.queue_draw()
        # self.zoom_fit()
        # self.tags_refresh()

    def onSelectionChanged(self):
        self.uiTagManager.onSelectionChanged()
        self.uiWorkArea.onSelectionChanged()

    def onItemTreeChanged(self):
        self.uiLevelSelector.onItemTreeChanged()
        self.uiItemFilter.onItemTreeChanged()
        if self.core.bulkMode:
            return

    def onContentChanged(self):
        self.uiWorkArea.onContentChanged()

    def onTagChanged(self):
        self.uiTagManager.onTagChanged()

    def onItemFocused(self):
        item = self.core.getCurrentItem()
        if not item:
            return
        self.uiItemList.onItemFocused(item)

    def onItemBlurred(self, item):
        if not item:
            return
        self.uiItemList.onItemBlurred(item)