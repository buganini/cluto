#!/usr/bin/env python

from ctieUI import *

if __name__ == "__main__":
	app = CtieUI()
	Gtk.main()
	if clear_tempdir and tempdir:
		os.execvp("rm",["rm","-rf",tempdir])
