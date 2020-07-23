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
