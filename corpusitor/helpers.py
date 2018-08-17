import os
import tempfile
import re

def try_int(s):
	try: return int(s)
	except: return s

def natsort_key(s):
	return map(try_int, re.findall(r'(\d+|\D+)', s))

def natcmp(a, b):
	return cmp(natsort_key(a), natsort_key(b))

tempdir=None
def get_tempdir():
	global tempdir
	if not tempdir or not os.path.exists(tempdir):
		tempdir=tempfile.mkdtemp(prefix='ctie_')
	return tempdir
