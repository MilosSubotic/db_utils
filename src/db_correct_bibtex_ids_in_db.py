#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Correct BibTeX ID in `BibTeX_ID` and `BibTeX`.
'''

###############################################################################

from __future__ import print_function

__author__      = 'Milos Subotic'
__email__       = 'milos.subotic.sm@gmail.com'
__copyright__   = 'MIT'

###############################################################################

import os
import argparse
import sqlite3
from common.utils import *
msg_print_type(False)
from common.db_finder import *

import bibtexparser as bib
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

###############################################################################

def link_to_url(b):
	if 'link' in b:
		b['url'] = b['link']
		del b['link']
	return b

def create_parser():
	parser = BibTexParser()
	parser.ignore_nonstandard_types = False
	parser.homogenize_fields = False
	return parser

def correct_bibtex(bs, bibtex_id):
	if bs:
		# Update existing BibTeX.
		bd = bib.loads(bs, create_parser())
		if len(bd.entries) == 0:
			msg(ERROR, 'Cannot parse BibTeX')
			return bs	
		b = bd.entries[0]
		b['ID'] = bibtex_id
		link_to_url(b)
	else:
		return bs
	
	bw = BibTexWriter()
	bw.indent = '  '
	bs = bw.write(bd)
	
	return bs

def correct_bibtex_ids():
	print('Creating/updating BibTeX in DB file: ', db_file)

	con = sqlite3.connect(db_file)
	cur = con.cursor()

	cur.execute("select `Title`, `BibTeX`, `BibTeX_ID` from `Papers`")
	t1 = cur.fetchall()
	titles = [tt[0] for tt in t1]
	bibtexs = [tt[1] for tt in t1]
	bibtex_ids = [tt[2] for tt in t1]
	
	r = range(len(titles))
	
	for idx in r:
		bibtex_id = bibtex_ids[idx]
		if bibtex_id:
			new_bibtex_id = bibtex_id.replace('.', '_')
			if new_bibtex_id != bibtex_id:
				bibtex_id = new_bibtex_id
				bibtex_ids[idx] = bibtex_id
				bibtexs[idx] = correct_bibtex(bibtexs[idx], bibtex_id)

	for idx in r:
		cur.execute(
			"update `Papers` set `BibTeX_ID`=?, `BibTeX`=? where `Title`=?",
			(bibtex_ids[idx], bibtexs[idx], titles[idx])
		)

	con.commit()
	con.close()


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description = __doc__
	)
	args = parser.parse_args()
	
	correct_bibtex_ids()
	
###############################################################################
