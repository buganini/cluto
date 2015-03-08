#!/usr/bin/env python

from ctie import *

if __name__ == "__main__":
	app = CTIE()
	Gtk.main()
	if clear_tempdir and tempdir:
		os.execvp("rm",["rm","-rf",tempdir])
