#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Move files from hunt place to directory in tree and update DB.
'''

###############################################################################

from __future__ import print_function

__author__	    = 'Stefan Maretic, Milos Subotic'
__email__	    = 'milos.subotic.sm@gmail.com'
__copyright__   = 'MIT'

###############################################################################

import os
import sys
import shutil
import glob
import sqlite3
import argparse
from common.common import *

from os.path import join, dirname, relpath, basename

###############################################################################

def fill_db(src, dst):
	d = relpath(dst, root_dir)
	f = basename(src)
	title_field = os.path.splitext(f)[0]
	file_field = join(d, f)
	splited_src_dir = dirname(src).split('/')
	
	fields = {
		'`File`'             : file_field,
		'`Where_searched`'   : None,
		'`Search_keywords`'  : None,
		'`Reference_from`'   : None,
		'`Because_it_cited`' : None
	}
	because_it_cited_field = None
	reason = splited_src_dir[-2]
	d1 = splited_src_dir[-1]
	if reason == 'kw':
		s = d1.split(' - ')
		fields['`Search_keywords`'] = d1
		fields['`Where_searched`'] = 'Google Scholar'
		if len(s) >= 2:
			ws = s[-1]
			if ws in ['google.com']:
				fields['`Where_searched`'] = ws
				fields['`Search_keywords`'] = ' - '.join(s[0:-1])
	elif reason == 'ref' or reason == 'refs':
		fields['`Reference_from`'] = d1
	elif reason == 'cites':
		fields['`Because_it_cited`'] = d1
	else:
		reason = None
	
	print('`Title` = ', title_field)
	for field_name, field_value in fields.items():
		if field_value:
			print('`{0}` = {1}'.format(field_name, field_value))
	
	con = sqlite3.connect(db_file)
	cur = con.cursor()

	cur.execute("select `Title` from `Papers`")
	titles = [ t[0] for t in cur.fetchall()]
	
	already_exists = False
	for t in titles:
		t2 = t.replace(':', ' -').replace('/', '~')
		if t2 == title_field:
			title_field = t
			already_exists = True
			break

	
	if already_exists:
		# If there is no new value for field, use that alredy in table.
		
		for field_name in fields.keys():
			if not fields[field_name]:
				cur.execute(
					"select `{0}` from `Papers` where `Title`=?".format(
						field_name
					),
					(title_field,)
				)
				fields[field_name] = cur.fetchall()[0][0]
		
		query = "update `Papers` set "
		l = []
		for field_name, field_value in fields.items():
			query += field_name + "=?, "
			l.append(field_value)
		query += "where `Title`=?"
		l.append(title_field)
		
		cur.execute(
			query,
			tuple(l)
		)
	else:
		query = "insert into `Papers` ("
		l = []
		for field_name, field_value in fields.items():
			query += field_name + ", "
			l.append(field_value)
		query += "`Title`) values ("
		query += '?, ' * len(fields)
		query += "?)"
		l.append(title_field)
		
		cur.execute(
			query,
			tuple(l)
		)
	
	con.commit()
	con.close()

def move_from_hunt_to_tree(src, dst):
	src = correct_path(src)
	dst = correct_path(dst)
	
	if not file_exists(src):
		error('No source or not file: ', src)
	
	dst_file = join(dst, basename(src))
	if file_exists(dst_file):
		error('Destination file already exists: ', dst_file)
		
	mkdir_p(dst)
	shutil.move(src, dst)
	
	fill_db(src, dst)

def move_files(src, dst):
	srcs = []
	for s in src:
		srcs += glob.glob(s)
	if len(srcs) == 0:
		print('Nothing to move from source: ', src)
	else:
		for s in srcs:
			move_from_hunt_to_tree(s, dst)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description = __doc__
	)
	parser.add_argument(
		'src',
		metavar = 'src',
		type = str,
		nargs = '+',
		help = 'source files'
	)
	parser.add_argument(
		'dst',
		metavar = 'dst',
		type = str,
		nargs = 1,
		help = 'destination directory'
	)
	args = parser.parse_args()
	
	move_files(args.src, args.dst[0])

###############################################################################
