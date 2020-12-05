#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
From `BibTeX` update other fields: `Title`, `Journal`, `Year`...
'''

###############################################################################

from __future__ import print_function

__author__      = 'Milos Subotic'
__email__       = 'milos.subotic.sm@gmail.com'
__copyright__   = 'MIT'

###############################################################################

import os
import sys
import errno
import shutil
import glob
import sqlite3
import argparse

from common.utils import *
from common.db_finder import *

import bibtexparser as bib
from bibtexparser.bparser import BibTexParser

###############################################################################

db_to_bib_fields = {
	'Title' : ['title'],
	'Journal_Conference_Other_Source' : ['journal', 'booktitle'],
	'Year' : ['year'],
	'BibTeX_ID' : ['ID']
}

###############################################################################
	
def create_parser():
	parser = BibTexParser()
	parser.ignore_nonstandard_types = False
	parser.homogenize_fields = False
	return parser

def update_fields():

	fields_table = []
	title_idx = None
	for (i, (d, b)) in enumerate(db_to_bib_fields.items()):
		if d == 'Title':
			title_idx = i
		fields_table.append((i, d, b))
	assert title_idx != None

	con = sqlite3.connect(db_file)
	cur = con.cursor()
	
	fts = "" # Fields to select.
	for (i, d, b) in fields_table:
		fts += "`" + d + "`, "
	
	cur.execute("select {0}`File`, `BibTeX` from `Papers`".format(fts))
	for rec in cur.fetchall():
		# Update record.
		bibtex = rec[-1]
		file_path = rec[-2]

		# If have that autoincrementing number for a title,
		# update it no matter it is not blank.
		update_title = rec[title_idx].isdigit()


		if bibtex:
			# Have BibTeX.

			if all(rec[0:-1]) and not update_title:
				# No empty fields to update.
				continue

			bd = bib.loads(bibtex, create_parser())
			if len(bd.entries) == 0:
				# Cannot parse BibTeX.
				continue
			be = bd.entries[0]


			title = be['title'].replace('{', '').replace('}', '')
			print('\nUpdating: ', title)
			for (i, d, b) in fields_table:
				is_title = i == title_idx
				field_empty_in_db = not rec[i]
				field_in_bibtex = None
				for bb in b:
					if bb in be:
						field_in_bibtex = bb
						break
					
				# If need to update title do it anyway. 
				# 100% that it has title field in DB and BibTeX.
				if (field_empty_in_db and field_in_bibtex) or \
					(is_title and update_title):
				
					# Field exists.
					field = be[field_in_bibtex]\
						.replace('{', '')\
						.replace('}', '')
					# DB and BibTeX different?
					if rec[i] != field:
						# Print difference.
						print(d, ': ', rec[i], ' -> ', field)

						cur.execute(
							"update `Papers` set `{0}`=? "
								"where `BibTeX`=?".format(d), 
							(field, bibtex)
						)
				elif field_empty_in_db and not field_in_bibtex:
					print('Missing field(s) in BibTeX: ', b)
		elif file_path:
			# Have File.
			if update_title:
				# Extract Title from File.
				base = os.path.basename(file_path)
				new_title = os.path.splitext(base)[0]
				old_title = rec[title_idx]
				
				cur.execute(
					"update `Papers` set `Title`=? "
						"where `Title`=?".format(d), 
					(new_title, old_title)
				)


	# Comment to emulate.	
	con.commit()
	con.close()
	

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description = __doc__
	)
	args = parser.parse_args()
	
	update_fields()
	
###############################################################################
