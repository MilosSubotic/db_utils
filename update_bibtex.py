#!/usr/bin/env python
# -*- coding: utf-8 -*-
#FIXME For now work with python2,
# because python 3.2 cannot use bibtexparser.

'''
Create/update `BibTeX` in database with crossref.org online version.
Counting start from 1.
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
import re

import bibtexparser as bib
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

import requests

###############################################################################

titles_to_ignore = [
	'A Frequency-hopping Approach For Microwave Imaging Of Large Inhomogeneous Bodies',
	'Adaptive Coordinate Descent'
]
special_words = [
	'2D', '3D', 'FDTD', '(FDTD)', 'EC', '(EC)', 'openEMS', 'openEMS--a',
	'GHz', 'TM', 'TE', 'GA', 'PSO', 'FPGA', 'Lorentzian', 'Debye', 'Born',
	'CMA-ES', '(CMA-ES)'
]

###############################################################################

def create_parser():
	parser = BibTexParser()
	parser.ignore_nonstandard_types = False
	parser.homogenize_fields = False
	return parser

def link_to_url(b):
	if 'link' in b:
		b['url'] = b['link']
		del b['link']
	return b

def diff_bibs(b1, b2):
	ks = set(b1.keys()).union(set(b2.keys()))
	for k in ks:
		if k not in b1 and k in b2:
			print('Added: ', k, ' = ', b2[k])
		elif k in b1 and k not in b2:
			print('Removed: ', k, ' = ', b1[k])
		elif k in b1 and k in b1:
			if b1[k] != b2[k]:
				if k == 'url':
					print('\n\nURL changed!\n\n')
				print('Changed: ', k, ' = ', b1[k], ' -> ', b2[k])
		else:
			raise AssertError('Canont be here!')

#TODO Better.
def titlize(s):
	w = []
	for t in s.split(' '):
		upcase = sum(1 for c in t if c.isupper())
		alpha = sum(1 for c in t if c.isalpha())
		dots = sum(1 for c in t if c == '.')
		if alpha != dots:
			# Not initials.
			if upcase == alpha:
				# All uppcase.
				w.append(t.capitalize())
			else:
				w.append(t[0].upper() + t[1:])
		else:
			w.append(t)
	s = ' '.join(w)
	return s

def preserve_special_words(s):
	w = []
	for t in s.split(' '):
		tl = t.lower()
		for k in special_words:
			if tl == k.lower():
				t = '{' + k + '}'
				break
		w.append(t)
	s = ' '.join(w)
	return s
	
def correct_author(t):
	return titlize(t).replace(' And ', ' and ')\
		.replace('Van Den Berg', 'van den Berg')\
		.replace(u'ö', '{\\"o}')\
		.replace(u'ü', '{\\"u}')\
		

def correct_title(t):
	t = t.replace(r'&#x2013;', '--')\
		.replace(r'{\&}{\#}x2013$\mathsemicolon$', '--')\
		.replace(r'\textquotesingle', "'")\
		.replace(r'\textasciigrave', "`")\
		.replace(' - ', '--')
	t = t.replace(r'{`}', '`')\
		.replace(r"{'}", "'")
	t = t.replace(r'`` ', '')\
		.replace(r"''", '')

	#TODO Correct upcase titles.
	t = t.replace('{', '').replace('}', '')
	
	t =  titlize(t)

	t = preserve_special_words(t)
	
	return t

def prep_title(t):
	return correct_title(t.lower().replace('{', '').replace('}', ''))
			
def eq_titles(t1, t2):
	return prep_title(t1) == prep_title(t2)

def update_bibtex_string(i, bs1):
	# Update existing BibTeX.
	assert bs1
	
	bd1 = bib.loads(bs1, create_parser())
	if len(bd1.entries) == 0:
		# Cannot parse BibTeX.
		return bs1

	title = bd1.entries[0]['title']
	
	if correct_title(title) in titles_to_ignore:
		return bs1
	
	def intro():
		print()
		print(i, ' update:')
		print(title)
	
	#params = {'query.title' : title, 'rows': '1'}
	params = {'query' : title, 'rows': '10'}
	r1 = requests.get('http://api.crossref.org/works', params=params)
	if r1.status_code != 200:
		intro()
		print(r1.status_code)
		print(r1.url)
		return bs1
	
	a = r1.json
	assert a['status'] == 'ok'

	doi = None
	for it in a['message']['items']:
		if len(it['title']) != 0:
			if eq_titles(title, it['title'][0]):
				doi = it['DOI']
				break

	if not doi:
		intro()
		print('Cannot find title!')
		print('First match title:')
		print(a['message']['items'][0]['title'][0])
		print(r1.url)
		return bs1
			
	r2 = requests.get(
		'http://api.crossref.org/works/' + doi + 
		'/transform/application/x-bibtex'
	)
	if r2.status_code != 200:
		intro()
		print(r2.status_code)
		print(r2.url)
		return bs1
	
	bs2 = r2.content.decode('utf-8')
	bd2t = bib.loads(bs2, create_parser())
	
	bd2 = BibDatabase()
	bd2.entries = [bd2t.entries[0]]
	b1 = bd1.entries[0]
	b2 = bd2.entries[0]

	
	if 'title' not in b2:
		intro()
		print('Strange results!')
		print(b2)
		print(r1.url)
		print(r2.url)
		return bs1
	
	b2['ID'] = b1['ID']
	
	b2['title'] = correct_title(b2['title'])
	b2['author'] = correct_author(b2['author'])
	
	link_to_url(b1)
	link_to_url(b2)
	if 'url' in b1:
		b2['url'] = b1['url']
	else:
		b2['url'] = b2['url'].replace('%2F', '/')
	
	if b1 == b2:
		# Nothing new.
		return bs1

	intro()
	diff_bibs(b1, b2)
	
	bw = BibTexWriter()
	bw.indent = '  '
	bs2 = bw.write(bd2)
		
	return bs2


def create_bibtex_string(i, title):
	# Download new BibTeX.
	
	if correct_title(title) in titles_to_ignore:
		return None
	
	def intro():
		print()
		print(i, ' create:')
		print(title)
	
	#params = {'query.title' : title, 'rows': '1'}
	params = {'query' : title, 'rows': '10'}
	r1 = requests.get('http://api.crossref.org/works', params=params)
	if r1.status_code != 200:
		intro()
		print(r1.status_code)
		print(r1.url)
		return None
	
	a = r1.json
	assert a['status'] == 'ok'

	doi = None
	for it in a['message']['items']:
		if 'title' in it and len(it['title']) != 0:
			if eq_titles(title, it['title'][0]):
				doi = it['DOI']
				break

	if not doi:
		intro()
		print('Cannot find title!')
		print('First match title:')
		print(a['message']['items'][0]['title'][0])
		print(r1.url)
		return None
			
	r2 = requests.get(
		'http://api.crossref.org/works/' + doi + 
		'/transform/application/x-bibtex'
	)
	if r2.status_code != 200:
		intro()
		print(r2.status_code)
		print(r2.url)
		return None
	
	bs2 = r2.content.decode('utf-8')
	bd2t = bib.loads(bs2, create_parser())
	
	bd2 = BibDatabase()
	bd2.entries = [bd2t.entries[0]]
	b2 = bd2.entries[0]

	
	if 'title' not in b2:
		intro()
		print('Strange results!')
		print(b2)
		print(r1.url)
		print(r2.url)
		return None
	
	b2['ID'] = 'TODO_' + b2['ID']
	
	b2['title'] = correct_title(b2['title'])
	if 'author' in b2:
		b2['author'] = correct_author(b2['author'])
	else:
		b2['author'] = 'TODO'
	
	link_to_url(b2)
	if 'url' in b2:
		b2['url'] = b2['url'].replace('%2F', '/')
	else:
		b2['url'] = 'TODO'
	
	intro()
	for (k, v) in b2.items():
		print('Added: ', k, ' = ', v)
	
	bw = BibTexWriter()
	bw.indent = '  '
	bs2 = bw.write(bd2)
	
	return bs2


	
def update_bibtex_range(range_start, range_end):
	print('Creating/updating BibTeX in DB file: ', db_file)
	
	con = sqlite3.connect(db_file)
	cur = con.cursor()
	
	cur.execute("select `Title`, `BibTeX` from `Papers`")
	t1 = cur.fetchall()
	titles = [tt[0] for tt in t1]
	bibtexes = [tt[1] for tt in t1]
	
	# Search range.
	def entry_to_idx(entry):
		i = int(entry)
		if i <= 0 or i > len(titles):
			error('Index ', i, ' is out of range for DB!')
		idx = i-1
		return idx
	
	print('In range: [', range_start, ', ', range_end, '] (closed interval)')
	
	start_idx = entry_to_idx(range_start)
	end_idx = entry_to_idx(range_end)
	r = range(start_idx, end_idx+1)
	
	for idx in r:
		i = idx+1
		if bibtexes[idx]:
			bibtexes[idx] = update_bibtex_string(i, bibtexes[idx])
		else:
			bibtexes[idx] = create_bibtex_string(i, titles[idx])
	
	for i in r:
		cur.execute(
			"update `Papers` set `BibTeX`=? where `Title`=?",
			(bibtexes[i], titles[i])
		)
		
	con.commit()
	con.close()
	

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description = __doc__
	)
	parser.add_argument(
		'entry_or_range_start',
		metavar = 'entry_or_range_start',
		type = int,
		nargs = 1,
		help = 'alone entry or range start'
	)
	parser.add_argument(
		'range_end',
		metavar = 'range_end',
		type = int,
		nargs = '?',
		help = 'range end including this one'
	)
	args = parser.parse_args()
	
	if args.range_end:
		update_bibtex_range(
			args.entry_or_range_start[0],
			args.range_end
		)
	else:
		update_bibtex_range(
			args.entry_or_range_start[0],
			args.entry_or_range_start[0]
		)

###############################################################################

