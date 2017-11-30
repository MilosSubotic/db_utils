#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Search and list papers from tree which are not in DB.
'''

###############################################################################

from __future__ import print_function

__author__	    = 'Stefan Maretic, Milos Subotic'
__email__	    = 'milos.subotic.sm@gmail.com'
__copyright__   = 'MIT'

###############################################################################

import os
import sys
import errno
import shutil
import glob
import sqlite3
import argparse

from common.common import *
from os.path import join

###############################################################################

exts = ['.pdf', '.html', '.ps', '.ps.gz']
#search_dirs = ['Papers', 'Numeric', 'Books']
search_dirs = ['Papers', 'Books']
#TODO .dbignore
ignores = [
	'Papers/home.cc.umanitoba.ca_EMILab'
]

###############################################################################

def list_non_added_papers():
	found_files = []
	for ext in exts:
		pattern = '*' + ext
		for d in search_dirs:
			found_files += recursive_glob(pattern, join(root_dir, d))
		
	found_files = [os.path.relpath(f, root_dir) for f in found_files]
	
	found_files2 = found_files
	found_files = []
	for f in found_files2:
		for i in ignores:
			if not f.startswith(i):
				found_files.append(f)
	
	con = sqlite3.connect(db_file)
	cur = con.cursor()
	cur.execute('select "File" from "Papers"')
	files_in_db = [t[0] for t in cur.fetchall()]
	con.close()
	
	for f in found_files:
		if f not in files_in_db:
			print(f)
	

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description = __doc__
	)
	args = parser.parse_args()
	
	list_non_added_papers()
	
###############################################################################

