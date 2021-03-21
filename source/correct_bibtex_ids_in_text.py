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
from common.utils import *
msg_print_type(False)
import re

###############################################################################


def create_parser():
	parser = BibTexParser()
	parser.ignore_nonstandard_types = False
	parser.homogenize_fields = False
	return parser

def correct_bibtex_ids(fn, en_replace_cites_in_brackets):

	with open(fn, 'r') as f:
		s = f.read()
		
	to_replace = {}
	
	cites = re.findall(r'\\cite{.*}', s)
	for cite in cites:
		m = re.match(r'\\cite{(.*)}', cite)
		assert(m)
		bibtex_id = m[1]
		new_bibtex_id = bibtex_id.replace('.', '_')
		if new_bibtex_id != bibtex_id:
			new_cite = r'\cite{' + new_bibtex_id + '}'
			to_replace[cite] = new_cite
	if en_replace_cites_in_brackets:
		cites = re.findall(r'\[.*\]', s)
		for cite in cites:
			m = re.match(r'\[(.*)\]', cite)
			assert(m)
			bibtex_id = m[1]
			new_bibtex_id = bibtex_id.replace('.', '_')
			if new_bibtex_id != bibtex_id:
				new_cite = r'[' + new_bibtex_id + ']'
				to_replace[cite] = new_cite
	
	for old, new in to_replace.items():
		s = s.replace(old, new)
	
	with open(fn, 'w') as f:
		f.write(s)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description = __doc__
	)
	parser.add_argument(
		'fns',
		metavar = 'fns',
		type = str,
		nargs = '+',
		help = 'text files'
	)
	parser.add_argument(
		'--en-replace-cites-in-brackets',
		dest = 'en_replace_cites_in_brackets',
		action = 'store_true',
		help = 'Replace cites in []'
	)
	args = parser.parse_args()
	
	for fn in args.fns:
		correct_bibtex_ids(fn, args.en_replace_cites_in_brackets)
	
###############################################################################
