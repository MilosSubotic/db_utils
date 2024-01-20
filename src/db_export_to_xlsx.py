#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Export DB to XLSX file.
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
from common.db_finder import *

from openpyxl import Workbook

###############################################################################

xlsx_file = os.path.splitext(os.path.os.path.basename(db_file))[0] + '.xlsx'

###############################################################################
	
def export_to_xlsx():
	print('Exporting DB file: ', db_file)
	print('to XLSX file: ', xlsx_file)
	
	con = sqlite3.connect(db_file)
	cur = con.cursor()
	
	#cur.execute("select `name` from `sqlite_master` where `type`='table'")
	#print(cur.fetchall())
	
	table = 'Papers'
	cur.execute("select * from `{}`".format(table))
	col_names = [description[0] for description in cur.description]
	t = cur.fetchall()
	#titles = [tt[0] for tt in t]
	
	wb = Workbook()
	sh = wb.active
	sh.title = table
	
	sh.append(col_names)
	
	for tt in t:
		sh.append(tt)
	
	wb.save(xlsx_file)
	
	con.close()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description = __doc__
	)
	args = parser.parse_args()

	export_to_xlsx()

###############################################################################
