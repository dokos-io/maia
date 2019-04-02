# Copyright (c) 2018, DOKOS and Contributors

import frappe
from tempfile import mkstemp
from shutil import move, rmtree
import os
from os import fdopen, remove
import json

def delete_standard_config_files():
	config_files = ["accounts", "setup"]

	for app in ["erpnext", "frappe"]:
		for config_file in config_files:

			target = frappe.get_app_path(app, "config", config_file + ".py")
			target_pyc = frappe.get_app_path(app, "config", config_file + ".pyc")
			try:
				if os.path.exists(target):
					remove(target)
				if os.path.exists(target_pyc):
					remove(target_pyc)
			except Exception as e:
				print(e)
				frappe.log_error(e, "Config Files Deletion")

def delete_erpnext_hooks():
	erpnext_hooks = frappe.get_app_path("erpnext", "hooks.py")

	patterns = ['setup_wizard_requires = ', 'setup_wizard_stages = ', 'setup_wizard_test = ', 'calendars = ', 'get_help_messages = ', 'get_user_progress_slides = ',
				'update_and_get_user_progress = ', 'email_brand_image = ', 'default_mail_footer = ', 'standard_portal_menu_items = ', 'error_report_email = ', 'domains = ']

	subst = ''
	for pattern in patterns:
		try:
			replace(erpnext_hooks, pattern, subst)
		except Exception as e:
			print(e)
			frappe.log_error(e, "ERPNext Hooks Deletions")

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

	# Load Standard Letters
	frappe_file = frappe.get_app_path("frappe", "model", "sync.py")

	pattern = "'print_format'"
	subst = "'print_format', 'maia_standard_letter'"
	try:
		replace(frappe_file, pattern, subst)
	except Exception as e:
		print(e)
		frappe.log_error(e, "Frappe Files Modifications - Standard Letter Loading")


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
	delete_standard_config_files()
	delete_erpnext_hooks()
	modify_frappe_files()
