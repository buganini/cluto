#!/usr/bin/env python

from QtUI import *

if __name__ == "__main__":
	app = CtieUI()
	if clear_tempdir and tempdir:
		os.execvp("rm",["rm","-rf",tempdir])
