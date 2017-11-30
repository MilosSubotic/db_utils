#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Add paper to DB.
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
import sqlite3
import argparse
from common.common import *

from os.path import join, dirname, relpath, basename

###############################################################################

def add_file_to_db(src):
	d = dirname(relpath(src, root_dir))
	f = basename(src)
	title_field = os.path.splitext(f)[0]
	file_field = join(d, f)
	
	print('"Title" = ', title_field)
	print('"File" = ', file_field)
	
	con = sqlite3.connect(db_file)
	cur = con.cursor()

	cur.execute('select "Title" from "Papers"')
	titles = [ t[0] for t in cur.fetchall()]
	
	already_exists = False
	for t in titles:
		t2 = t.replace(':', ' -').replace('/', '~')
		if t2 == title_field:
			title_field = t
			already_exists = True
			break
	
	if already_exists:
		cur.execute(
			'update "Papers" set "File"=? where "Title"=?', 
			(file_field, title_field)
		)
	else:
		cur.execute(
			'insert into "Papers" ("File", "Title") values (?, ?)',
			(file_field, title_field)
		)
	
	con.commit()
	con.close()

def add_files_to_db(files):
	for f in files:
		if not file_exists(f):
			error('No source or not file: ', f)
		add_file_to_db(f)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description = __doc__
	)
	parser.add_argument(
		'files',
		metavar = 'files',
		type = str,
		nargs = '+',
		help = 'files to add into a DB'
	)
	args = parser.parse_args()
	
	add_files_to_db(args.files)

###############################################################################

