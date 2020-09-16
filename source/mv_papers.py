#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Move files from hunt place to directory in tree and update DB.
'''

###############################################################################

from __future__ import print_function

__author__	    = 'Milos Subotic, Stefan Maretic'
__email__	    = 'milos.subotic.sm@gmail.com'
__copyright__   = 'MIT'

###############################################################################

import os
import sys
import shutil
import glob
import subprocess
import sqlite3
import argparse
from common.utils import *
msg_print_type(False)
from common.db_finder import *

from os.path import join, dirname, basename, relpath, isdir

###############################################################################

def file_name_to_title(file_name):
	title = file_name
	def warn_about(fn_code):
		if fn_code in file_name:
			warn('Has "', fn_code, '" in file name.')
	def warn_about2(fn_code):
		fn_code2 = fn_code + fn_code
		if fn_code in file_name and not (fn_code2 in file_name):
			warn('Has "', fn_code, '" in file name.')
	
	warn_about('<')
	warn_about('>')
	title = title.replace('..', ':')
	title = title.replace('\'\'', '\"')
	title = title.replace('~~', '/')
	title = title.replace('^^', '?')
	warn_about2('~')
	warn_about2('^')
	warn_about('\\')
	warn_about('|')
	warn_about('*')
	
	return title

def diff_fields(f1, f2):
	ks = set(f1.keys()).union(set(f2.keys()))
	for k in ks:
		if k not in f1 and k in f2:
			msg(DEBUG, 'Added: ', k, ' = ', f2[k])
		elif k in f1 and k not in f2:
			msg(WARN, 'Removed: ', k, ' = ', f1[k])
		elif k in f1 and k in f1:
			if f1[k] != f2[k]:
				if k == 'url':
					msg(WARN, '\n\nURL changed!\n\n')
				msg(INFO, 'Changed: ', k, ' = ', f1[k], ' -> ', f2[k])
		else:
			raise AssertError('Cannot be here!')

def fill_db(src, dst):
	d = relpath(dst, root_dir)
	f = basename(src)
	new_title = file_name_to_title(os.path.splitext(f)[0])
	file_field = join(d, f)
	splited_src_dir = dirname(src).split('/')
	
	new_fields = {
		'`File`' : file_field
	}
	because_it_cited_field = None
	if len(splited_src_dir) >= 2:
		reason = splited_src_dir[-2]
		d1 = splited_src_dir[-1]
		if reason == 'kw':
			new_fields['`Search_keywords`'] = d1
			new_fields['`Where_searched`'] = 'Google Scholar'
			s = d1.split(' - ')
			if len(s) >= 2:
				ws = s[-1]
				sk = ' - '.join(s[0:-1])
				if ws in ['google.com', 'Wiki']:
					new_fields['`Where_searched`'] = ws
					new_fields['`Search_keywords`'] = sk
		elif reason == 'ref' or reason == 'refs':
			new_fields['`Reference_from`'] = d1
		elif reason == 'cites':
			new_fields['`Because_it_cited`'] = d1
		else:
			reason = None

	con = sqlite3.connect(db_file)
	cur = con.cursor()

	cur.execute("select `Title`, `Index` from `Papers`")
	t1 = cur.fetchall()
	titles = [tt[0] for tt in t1]
	
	already_exists = False
	i = len(titles) + 1 # New one if inserting
	old_title = None
	for (idx, t) in enumerate(titles):
		if t.lower() == new_title.lower():
			if already_exists:
				msg(ERROR, 'Have multiple similar titles in database.')
			else:
				already_exists = True
				i = idx + 1
				old_title = t
				if old_title != new_title:
					msg(DEBUG, 'Same titles different in case!')
					msg(VERB, 'Existing:', old_title)
					msg(VERB, 'New:', new_title)
	
	
	old_fields = {}
	if already_exists:
		title = old_title
		if False:
			# Prefer new title.
			new_fields['`Title`'] = new_title
			
		for field_name in new_fields.keys():
			cur.execute(
				"select {0} from `Papers` where `Title`=?".format(
					field_name
				),
				(title,)
			)
			old_fields[field_name] = cur.fetchall()[0][0]
	else:
		title = new_title
		new_fields['`Title`'] = title
		new_fields['`Index`'] = i
	
	
	if already_exists:
		msg(INFO)
		msg(INFO, i, ' update:')
		msg(INFO, title)
	else:
		msg(DEBUG)
		msg(DEBUG, i, ' insert:')
		msg(DEBUG, title)
	diff_fields(old_fields, new_fields)
	
	if already_exists:
		query = "update `Papers` set "
		query += ", ".join([fn + "=?" for fn in new_fields.keys()])
		query += " where `Title`=?"
		
		cur.execute(
			query,
			tuple(list(new_fields.values()) + [title])
		)
	else:
		query = "insert into `Papers` ("
		query += ", ".join(new_fields.keys())
		query += ") values ("
		query += ", ".join(['?'] * len(new_fields))
		query += ")"
		
		cur.execute(
			query,
			tuple(new_fields.values())
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

def move_file(src, dst):
	move_from_hunt_to_tree(src, dst)

def move_dir(src, dst):
	src_root = os.path.normpath(join(src, '..'))
	# Move files.
	for root, dirs, files in os.walk(src):
		rel_root = relpath(root, src_root)
		dst_dir = join(dst, rel_root)
		if not isdir(dst_dir):
			os.mkdir(dst_dir)
		for f in files:
			src_file = join(root, f)
			move_file(src_file, dst_dir)
	
	# Check are dirs empty.
	for root, dirs, files in os.walk(src):
		assert(len(files) == 0)
		
	# Remove empty dirs.
	shutil.rmtree(src)

def move_glob(src, dst):
	srcs = []
	
	for s in src:
		# Escapaping [ and ].
		e = ''
		for c in s:
			if c == '[':
				e += '[[]'
			elif c == ']':
				e += '[]]'
			else:
				e += c
		srcs += glob.glob(e)
	if len(srcs) == 0:
		print('Nothing to move from source: ', src)
	else:
		for s in srcs:
			if isdir(s):
				move_dir(s, dst)
			else:
				move_file(s, dst)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description = __doc__
	)
	parser.add_argument(
		'src',
		metavar = 'src',
		type = str,
		nargs = '+',
		help = 'source files/directories'
	)
	parser.add_argument(
		'dst',
		metavar = 'dst',
		type = str,
		nargs = 1,
		help = 'destination directory'
	)
	args = parser.parse_args()
	
	move_glob(args.src, args.dst[0])

###############################################################################
