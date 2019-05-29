# Copyright (c) 2018, DOKOS and Contributors

import frappe
from tempfile import mkstemp
from shutil import move, rmtree
import os
from os import fdopen, remove
import json

def modify_frappe_files():

	# Different File
	frappe_file = frappe.get_app_path("frappe", "database", "mariadb", "database.py")

	pattern = "if self.user != 'root':"
	subst = "if self.user != 'root' and self.user != 'dokos_bdd':"
	try:
		replace(frappe_file, pattern, subst)
	except Exception as e:
		print(e)
		frappe.log_error(e, "Frappe Files Modifications")


def replace(file_path, pattern, subst):
	#Create temp file
	fh, abs_path = mkstemp()
	with fdopen(fh,'w') as new_file:
		with open(file_path) as old_file:
			for line in old_file:
				new_file.write(line.replace(pattern, subst))
	#Remove original file
	remove(file_path)
	#Move new file
	move(abs_path, file_path)

def before_migrate():
	modify_frappe_files()
