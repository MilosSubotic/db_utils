# -*- coding: utf-8 -*-

'''
'''

###############################################################################

from __future__ import print_function

__author__	    = 'Milos Subotic'
__email__	    = 'milos.subotic.sm@gmail.com'
__copyright__   = 'MIT'

###############################################################################

import os
import sys
import glob
import re
import inspect
import errno
import fnmatch

###############################################################################

d = os.getcwd()
while True:
	os.listdir(d)
	r = glob.glob(os.path.join(d, '*.sqlite'))
	if len(r) == 0:
		d2 = os.path.dirname(d)
		if d == d2:
			print('Not in DB tree!', file = sys.stderr)
			sys.exit(1)
		else:
			# Search futher.
			d = d2
	elif len(r) == 1:
		root_dir = d
		db_file = r[0]
		break
	else:
		print('More than one DB file!', file = sys.stderr)
		sys.exit(1)
		
###############################################################################

# Whole expression.
_debugRegex = re.compile(r'\bdebug\s*\(\s*(.*)\s*\)')

def debug(var):
	varName = ''
	for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
		m = _debugRegex.search(line)
		if m:
			varName = m.group(1)
			break
	print('{0} = {1}'.format(varName, var))

def error(*args, **kwargs):
	print('WARN: ', *args, file = sys.stderr, **kwargs)

def error(*args, **kwargs):
	print('ERROR: ', *args, file = sys.stderr, **kwargs)
	sys.exit(1)


def correct_path(path):
	return path.replace('\\', '/')
	
def file_exists(path):
	return os.path.isfile(path)

''' mkdir -p functionality:  '''
def mkdir_p(path):
	try:
		os.makedirs(path)
	except OSError as exc: # Python >2.5
		if exc.errno == errno.EEXIST and os.path.isdir(path):
			pass
		else:
			raise

def recursive_glob(pattern, directory = '.'):
	found = []
	for root, dirs, files in os.walk(str(directory), followlinks = True):
		dirs = map(lambda s: s + '/', dirs)
		for base_name in files:
			if fnmatch.fnmatch(base_name, pattern):
				found.append(os.path.join(root, base_name))
		for base_name in dirs:
			if fnmatch.fnmatch(base_name, pattern):
				found.append(os.path.join(root, base_name))			
	return found

###############################################################################