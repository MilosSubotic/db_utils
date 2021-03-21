#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Create/update `BibTeX` in database with online version.
'''

#TODO Remove \textquotesingle from others fields too.

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
import re

import bibtexparser as bib
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

import requests

from scholarly import scholarly, ProxyGenerator

###############################################################################

#POSSIBLE_TITLES_PRINT_NUM = 1 # Just first
POSSIBLE_TITLES_PRINT_NUM = 1000000 # All

unwanted_bib_keys = ['cites', 'gsrank', 'venue', 'eprint', 'abstract']

#TODO Nicer
titles_to_ignore = [
	'A Frequency-hopping Approach For Microwave Imaging Of Large Inhomogeneous Bodies',
	'Adaptive Coordinate Descent'
]

not_to_be_capitalized = [
	'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'in',
	'nor', 'of', 'on', 'or', 'the', 'to', 'up'
]
special_words = [
	'2D', '3D',
	'EM', 'FDTD', 'EC', 'openEMS', 'FBTS',
	'PML', 'CPML', 'CFS',
	'GHz', 'TM', 'TE', 'TEM', 'RF', 'UHF',
	'RCS', 'SAR',
	'UWB', 'EMC', 'EMI', 'MIMO',
	'CMA', 'ES', 'GA', 'PSO', 'ABC',
	'WCDA', 'TV',
	'CPU', 'FPGA', 'GPR', 'RAM', 'IRAM', 'VLSI', 'ASIC', 'CMOS',
	'GPU', 'CUDA',
	'ADC', 'DAC', 'GS',
	'CT', 'MRI',
	'others' #FIXME Bad if occurs in title.
]

###############################################################################

class Flags:
	pass

###############################################################################
# Proxy for scholarly.

__proxy = None
def __find_new_proxy():
	global __proxy
	while True:
		__proxy = ProxyGenerator()
		__proxy.FreeProxies()
		proxy_works = scholarly.use_proxy(__proxy)
		if proxy_works:
			break
	msg(VERB, 'Working proxy: ', __proxy)
	
def try_new_proxy():
	msg(VERB, 'Trying new proxy...')
	__find_new_proxy()
	
def init_proxy():
	global __proxy
	# Init proxy only if it is not already initialized.
	if not __proxy:
		msg(VERB, 'Initializing proxy...')
		__find_new_proxy()

###############################################################################

def parse_version(s):
	a = s.split('.')
	N = len(a)
	a = [int(aa) for aa in a]
	a = [v<<8*(N-1-i) for i, v in enumerate(a)]
	n = 0
	for aa in a:
		n |= aa
	#print(hex(n))
	return n

def get_json_from_request(r):
	#TODO Check version on old Debian.
	if parse_version(requests.__version__) >= parse_version('2.2.1'):
		return r.json()
	else:
		return r.json

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
			msg(DEBUG, 'Added: ', k, ' = ', b2[k])
		elif k in b1 and k not in b2:
			msg(WARN, 'Removed: ', k, ' = ', b1[k])
		elif k in b1 and k in b1:
			if b1[k] != b2[k]:
				if k == 'url':
					msg(WARN, '\n\nURL changed!\n\n')
				msg(INFO, 'Changed: ', k, ' = ', b1[k], ' -> ', b2[k])
		else:
			raise AssertError('Cannot be here!')

def capitalize(in_s, title_not_authors = True):
	#words = list(in_s.split(' '))
	words = []
	splits = []
	# 0 - word, 1 - splits
	state = 0
	w = ''
	s = ''
	for c in in_s:
		if state == 0:
			if c.isalpha() or c.isdigit():
				state = 0
				w += c
			else:
				state = 1
				s += c
				words.append(w)
				w = ''
		else:
			if c.isalpha() or c.isdigit():
				state = 0
				w += c
				splits.append(s)
				s = ''
			else:
				state = 1
				s += c
	# Flush.
	words.append(w)
	splits.append(s)
	# To have them even.
	if len(words) > len(splits):
		splits.append('')
	elif len(words) < len(splits):
		words.append('')
	
	def is_word_upcase(w):
		# Word upcase = all letters upcase.
		any_alpha = False
		for c in w:
			if c.isalpha():
				any_alpha = True
				if not c.isupper():
					return False
		return any_alpha
	def is_word_capitalized(w):
		return w.capitalize() == w
	def is_word_special(w):
		lw = w.lower()
		for sw in special_words:
			if lw == sw.lower():
				return True
		return False
	def get_special(w):
		lw = w.lower()
		for sw in special_words:
			if lw == sw.lower():
				return sw
		return None
	
	upcase = [is_word_upcase(w) for w in words]
	all_upcase = all(upcase)
	capitalized = [is_word_capitalized(w) for w in words]
	special = [is_word_special(w) for w in words]
	out_words = []
	
	for i in range(len(words)):
		w = words[i]
		u = upcase[i]
		c = capitalized[i]
		s = special[i]
		if s: # Special word.
			out_words.append('{' + get_special(w) + '}')
		elif u: # Upper word.
			if all_upcase:
				# Make all capitalize and hope we do not have any upcase word.
				if w.lower() in not_to_be_capitalized:
					if title_not_authors:
						if i == 0 or i == len(words)-1: # First or last.
							# Capitalize them no matter
							# if they are in not_to_be_capitalized.
							out_words.append(w.capitalize())
						else:
							out_words.append(w.lower())
					else:
						out_words.append(w)
				else:
					out_words.append(w.capitalize())
			else:
				if w.lower() in not_to_be_capitalized:
					if title_not_authors:
						if i == 0 or i == len(words)-1: # First or last.
							# Capitalize them no matter
							# if they are in not_to_be_capitalized.
							out_words.append(w.capitalize())
						else:
							msg(WARN, f'Word "{w}" was not lower!')
							out_words.append(w.lower())
					else:
						out_words.append(w)
				else:
					if len(w) != 1: # No need to warn on single letter stuff.
						# At this point it is not in special words, so:
						msg(WARN, f'Maybe add "{w}" to the special words!')
					if title_not_authors:
						out_words.append('{' + w + '}')
					else:
						if len(w) == 1:
							out_words.append(w)
						else:
							# Kind a strange.
							out_words.append('{' + w + '}')
		elif c: # Capitalized.
			if w.lower() in not_to_be_capitalized:
				if title_not_authors:
					if i == 0 or i == len(words)-1: # First or last.
						# Capitalize them no matter
						# if they are in not_to_be_capitalized.
						out_words.append(w)
					else:
						msg(WARN, f'Word "{w}" was not lower!')
						out_words.append(w.lower())
				else:
					out_words.append(w)
			else:
				out_words.append(w)
		else: # Lower word.
			if w in not_to_be_capitalized:
				if title_not_authors:
					if i == 0 or i == len(words)-1: # First or last.
						# Capitalize them no matter
						# if they are in not_to_be_capitalized.
						out_words.append(w.capitalize())
					else:
						out_words.append(w)
				else:
					out_words.append(w)
			else:
				out_words.append(w.capitalize())

	out_s = ''
	for w, s in zip(out_words, splits):
		out_s += w + s
	return out_s

def correct_author(t):
	t = t.replace(u'ö', '{\\"o}')\
		.replace(u'ü', '{\\"u}')\
		
	t = t.replace('{', '').replace('}', '')
	
	t = capitalize(t, False)
	
	t = t.replace('Van Den Berg', 'van den Berg')
	
	return t


def correct_title(t):
	t = t.replace(r'&#x2013;', '--')\
		.replace(r'{\&}{\#}x2013$\mathsemicolon$', '--')\
		.replace(r'\textquotesingle', "'")\
		.replace(r'\textasciigrave', "`")\
		.replace('–', '--')\
		.replace('—', '---')\
		.replace(r'\textendash', '-')\
		.replace(r'\textemdash', '--')
	t = t.replace(r'{`}', '`')\
		.replace(r"{'}", "'")
	t = t.replace(r'`` ', '')\
		.replace(r"''", '')
	t = t.replace(r'<title>', '')\
		.replace(r'</title>', '')\
		.replace(r'$\less$title$\greater$', '')\
		.replace(r'$\less$/title$\greater$', '')


	t = t.replace('{', '').replace('}', '')

	t = capitalize(t)

	return t

def eq_titles(t1, t2):
	ct1 = correct_title(t1.lower())
	ct2 = correct_title(t2.lower())
	# For debug.
	if False:
		print('"{}"'.format(ct1))
		print('"{}"'.format(ct2))
	return ct1 == ct2


def update_bibtex_string(
	flags,
	i,
	title,
	bid1,
	bs1
):
	msg(VERB, '')
	
	if bs1:
		# Update existing BibTeX.
		bd1 = bib.loads(bs1, create_parser())
		if len(bd1.entries) == 0:
			msg(ERROR, 'Cannot parse BibTeX')
			return bs1	
		b1 = bd1.entries[0]
	else:
		# Download new BibTeX.
		b1 = {}

	if correct_title(title) in titles_to_ignore:
		return bs1

	def intro():
		if bs1:
			msg(INFO, i, ' update:')
			msg(INFO, title)
		else:
			msg(DEBUG, i, ' insert:')
			msg(DEBUG, title)

	########
	
	def search_over_crossref_org():
		#params = {'query.title' : title, 'rows': '1'}
		params = {'query' : title, 'rows': '10'}
		r1 = requests.get('http://api.crossref.org/works', params=params)
		if r1.status_code != 200:
			intro()
			msg(ERROR, r1.status_code)
			msg(ERROR, r1.url)
			return None

		a = get_json_from_request(r1)
		assert a['status'] == 'ok'

		doi = None
		possible_titles = []
		for it in a['message']['items']:
			if 'title' in it and len(it['title']) != 0:
				# For testing.
				if len(it['title']) != 1:
					intro()
					msg(ERROR, 'Multiple titles on one entry')
				
				t = it['title'][0]
				possible_titles.append(t)
				if eq_titles(title, t):
					if doi:
						intro()
						msg(ERROR, 'Multiple same titles')
					else:
						doi = it['DOI']
					break

		if not doi:
			if not flags.ignore_miss:
				intro()
				msg(WARN, 'Cannot find title over crossref.org!')
				msg(VERB, 'url: ', r1.url)
				msg(VERB, 'Possible titles:')
				for pt in possible_titles[0:POSSIBLE_TITLES_PRINT_NUM]:
					msg(VERB, '\t', pt)
			return None

		r2 = requests.get(
			'http://api.crossref.org/works/' + doi +
			'/transform/application/x-bibtex'
		)
		if r2.status_code != 200:
			intro()
			msg(ERROR, r2.status_code)
			msg(ERROR, r2.url)
			return None

		bs2 = r2.content.decode('utf-8')
		return bs2

	def search_over_scholarly():
		bs2 = None
		b2_url = None
		
		query = None
		if flags.en_scholarly_proxy:
			init_proxy()
			#FIXME Nicer?
			#TODO Number of trials.
			while True:
				try:
					query = scholarly.search_pubs(title)
					break
				except Exception as e:
					try_new_proxy()
		else:
			try:
				query = scholarly.search_pubs(title)
			except Exception as e:
				intro()
				msg(WARN, 'Cannot connect with scholarly!')
				return bs2, b2_url
		
		possible_titles = []
		for i, pub in enumerate(query):
			if i == 1:
				break

			t = pub['bib']['title']
			possible_titles.append(t)
			if eq_titles(title, t):
				if bs2:
					intro()
					msg(ERROR, 'Multiple same titles')
				else:
					bs2 = scholarly.bibtex(pub)
					b2_url = pub['pub_url']
				pass
		
		if not bs2:
			if not flags.ignore_miss:
				intro()
				msg(WARN, 'Cannot find title with scholarly!')
				msg(VERB, 'Possible titles:')
				for pt in possible_titles[0:POSSIBLE_TITLES_PRINT_NUM]:
					msg(VERB, '\t', pt)
		
		return bs2, b2_url
		
	########
	
	bs2 = None
	b2_url = None
	if flags.en_crossref_org:
		if not bs2:
			bs2 = search_over_crossref_org()
	if flags.en_scholarly:
		if not bs2:
			bs2, b2_url = search_over_scholarly()
	if not bs2:
		# Nothing found.
		if bs1:
			# It is update.
			# Still, do some processing on existing bibtex.
			bs2 = bs1
		else:
			# It is insert.
			return bs1
	
	# Now have bs2.
	
	bd2t = bib.loads(bs2, create_parser())

	bd2 = BibDatabase()
	bd2.entries = [bd2t.entries[0]]
	b2 = bd2.entries[0]
	
	if 'title' not in b2:
		intro()
		msg(ERROR, 'Strange results!')
		msg(VERB, b2)
		msg(VERB, r1.url)
		msg(VERB, r2.url)
		return bs1
	
	for unwanted_key in unwanted_bib_keys:
		if unwanted_key in b2:
			del b2[unwanted_key]
	
	# Now have b2.
	
	if bid1:
		b2['ID'] = bid1
	else:
		if bs1:
			b2['ID'] = b1['ID']
		else:
			b2['ID'] = 'TODO_' + b2['ID']

	b2['title'] = correct_title(b2['title'])
	if 'author' in b2:
		b2['author'] = correct_author(b2['author'])

	link_to_url(b1)
	link_to_url(b2)
	if 'url' in b1:
		b2['url'] = b1['url']
	elif 'url' in b2:
		b2['url'] = b2['url'].replace('%2F', '/')
	elif b2_url:
		b2['url'] = b2_url.replace('%2F', '/')
	else:
		msg(WARN, 'No URL!')
	
	
	if b1 == b2:
		# Nothing new.
		return bs1

	intro()
	diff_bibs(b1, b2)

	bw = BibTexWriter()
	bw.indent = '  '
	bs2 = bw.write(bd2)

	return bs2


def update_bibtex_range(flags, range_start, range_end):
	print('Creating/updating BibTeX in DB file: ', db_file)

	con = sqlite3.connect(db_file)
	cur = con.cursor()

	cur.execute("select `Title`, `BibTeX`, `BibTeX_ID` from `Papers`")
	t1 = cur.fetchall()
	titles = [tt[0] for tt in t1]
	bibtexes = [tt[1] for tt in t1]
	bibtex_ids = [tt[2] for tt in t1]

	# Search range.
	def entry_to_idx(entry):
		i = int(entry)
		if i <= 0 or i > len(titles):
			error('Index ', i, ' is out of range for DB!')
		idx = i - 1
		return idx

	print('In range: [', range_start, ', ', range_end, '] (closed interval)')
	
	start_idx = entry_to_idx(range_start)
	end_idx = entry_to_idx(range_end)
	r = range(start_idx, end_idx + 1)

	for idx in r:
		i = idx + 1
		bibtexes[idx] = update_bibtex_string(
			flags,
			i,
			titles[idx],
			bibtex_ids[idx],
			bibtexes[idx]
		)

	for idx in r:
		cur.execute(
			"update `Papers` set `BibTeX`=? where `Title`=?",
			(bibtexes[idx], titles[idx])
		)

	con.commit()
	con.close()


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description = __doc__
	)
	parser.add_argument(
		'-i',
		'--ignore-miss',
		action = 'store_true',
		help = 'Ignore and do not report misses (Cannot find title)'
	)
	parser.add_argument(
		'--dis-crossref-org',
		dest = 'en_crossref_org',
		action = 'store_false',
		help = 'Disable searching on Crossref.org'
	)
	parser.add_argument(
		'--en-scholarly',
		dest = 'en_scholarly',
		action = 'store_true',
		help = 'Enable searching with Scholarly'
	)
	parser.add_argument(
		'--en-scholarly-proxy',
		dest = 'en_scholarly_proxy',
		action = 'store_true',
		help = 'Enable proxy for Scholarly'
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
	
	flags = Flags()
	flags.ignore_miss = args.ignore_miss
	flags.en_crossref_org = args.en_crossref_org
	flags.en_scholarly = args.en_scholarly
	flags.en_scholarly_proxy = args.en_scholarly_proxy
	if args.range_end:
		update_bibtex_range(
			flags,
			args.entry_or_range_start[0],
			args.range_end
		)
	else:
		update_bibtex_range(
			flags,
			args.entry_or_range_start[0],
			args.entry_or_range_start[0]
		)
	
###############################################################################
