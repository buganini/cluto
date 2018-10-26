#!/usr/bin/env python

import sys
from qt import MainUI
from cluto import Cluto

if __name__ == "__main__":
	argv = {}
	if len(sys.argv) > 1:
		argv["workspace"] = sys.argv[1]
	app = MainUI(Cluto, argv)