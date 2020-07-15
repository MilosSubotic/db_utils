#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Dump all non-empty, non-TODO `BibTeX` fields to 'References.bib' file.
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
from common.common import *

import bibtexparser as bib
from bibtexparser.bparser import BibTexParser

###############################################################################

cites_bib_file = 'References.bib'

###############################################################################

def create_parser():
	parser = BibTexParser()
	parser.ignore_nonstandard_types = False
	parser.homogenize_fields = False
	return parser
	
def dump_cites():
	print('Dumping BibTeX from DB file: ', db_file)
	print('to cite file: ', cites_bib_file)
	
	con = sqlite3.connect(db_file)
	cur = con.cursor()
	
	cur.execute("select `Title`, `BibTeX` from `Papers`")
	t1 = cur.fetchall()
	titles = [tt[0] for tt in t1]
	bibtexes = [tt[1] for tt in t1]
	
	con.close()
	
	with open(cites_bib_file, 'w') as f:
		for bs in bibtexes:
			if not bs:
				# Empty BibTeX string.
				continue

			bd = bib.loads(bs, create_parser())
			if len(bd.entries) == 0:
				# Cannot parse BibTeX.
				continue
				
			b = bd.entries[0]
			if b['ID'].startswith('TODO_'):
				continue
	
			f.write(bs)
			f.write('\n')
	

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description = __doc__
	)
	args = parser.parse_args()

	dump_cites()

###############################################################################
