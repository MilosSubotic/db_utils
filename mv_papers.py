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
	
	where_searched_field = None
	search_keywords_field = None
	reference_from_field = None
	reason = splited_src_dir[-2]
	d1 = splited_src_dir[-1]
	if reason == 'kw':
		s = d1.split(' - ')
		search_keywords_field = d1
		where_searched_field = 'Google Scholar'
		if len(s) >= 2:
			ws = s[-1]
			if ws in ['google.com']:
				where_searched_field = ws
				search_keywords_field = ' - '.join(s[0:-1])
	elif reason == 'ref':
		reference_from_field = d1
	else:
		reason = None
	
	print('"Title" = ', title_field)
	print('"File" = ', file_field)
	if where_searched_field:
		print('"Where_searched" = ', where_searched_field)
	if search_keywords_field:
		print('"Search_keywords" = ', search_keywords_field)
	if reference_from_field:
		print('"Reference_from" = ', reference_from_field)
	
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
		# If there is no new value for field, use that alredy in table.
		if not where_searched_field:
			cur.execute(
				'select "Where_searched" from "Papers" where "Title"=?',
				(title_field,)
			)
			where_searched_field = cur.fetchall()[0][0]
		if not search_keywords_field:
			cur.execute(
				'select "Search_keywords" from "Papers" where "Title"=?',
				(title_field,)
			)
			search_keywords_field = cur.fetchall()[0][0]
		if not reference_from_field:
			cur.execute(
				'select "Reference_from" from "Papers" where "Title"=?',
				(title_field,)
			)
			reference_from_field = cur.fetchall()[0][0]
		cur.execute(
			'update "Papers" set "File"=?, "Where_searched"=?, '\
				'"Search_keywords"=?, "Reference_from"=? where "Title"=?', 
			(file_field, where_searched_field, search_keywords_field, 
				reference_from_field, title_field)
		)
	else:
		cur.execute(
			'insert into "Papers" ("File", "Where_searched", '\
				'"Search_keywords", "Reference_from", "Title")'\
				' values (?, ?, ?, ?, ?)', 
			(file_field, where_searched_field, search_keywords_field, 
				reference_from_field, title_field)
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

