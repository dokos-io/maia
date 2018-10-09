# Copyright (c) 2018, DOKOS and Contributors

import frappe
from tempfile import mkstemp
from shutil import move, rmtree
import os
from os import fdopen, remove
import json


def remove_deletion_from_permissions():
	permission_manager = frappe.get_app_path("frappe", "core", "page", "permission_manager", "permission_manager.py")
	pattern = 'not_allowed_in_permission_manager = ["DocType", "Patch Log", "Module Def", "Transaction Log"]'
	subst = 'not_allowed_in_permission_manager = ["DocType", "Patch Log", "Module Def", "Transaction Log", "Deleted Document"]'

	try:
		replace(permission_manager, pattern, subst)
	except Exception as e:
		print(e)
		frappe.log_error(e, "Deleted Documents")

def prevent_company_reset():
	company_js = frappe.get_app_path("erpnext", "setup", "doctype", "company", "company.js")
	pattern = 'frm.get_field("delete_company_transactions").$input.addClass("btn-danger");'
	subst = 'frm.get_field("delete_company_transactions").$input.addClass("hidden");'

	try:
		replace(company_js, pattern, subst)
	except Exception as e:
		print(e)
		frappe.log_error(e, "Company JS")

	company_deletion = frappe.get_app_path("erpnext", "setup", "doctype", "company", "delete_company_transactions.py")
	company_deletion_pyc = frappe.get_app_path("erpnext", "setup", "doctype", "company", "delete_company_transactions.pyc")
	try:
		if os.path.exists(company_deletion):
			remove(company_deletion)
		if os.path.exists(company_deletion_pyc):
			remove(company_deletion_pyc)
	except Exception as e:
		print(e)
		frappe.log_error(e, "Company Deletion")

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

def delete_frappe_hooks():
	frappe_hooks = frappe.get_app_path("frappe", "hooks.py")

	patterns = ['app_email = "info@frappe.io"', '"frappe.utils.change_log.check_for_update"']

	subst = ''
	for pattern in patterns:
		try:
			replace(frappe_hooks, pattern, subst)
		except Exception as e:
			print(e)
			frappe.log_error(e, "Frappe Hooks Deletions")

def modify_frappe_files():
	# Different File
	frappe_file = frappe.get_app_path("frappe", "desk", "page", "modules", "modules.js")

	pattern = 'frappe.get_desktop_icons(true)'
	subst = 'frappe.get_desktop_icons(false)'
	try:
		replace(frappe_file, pattern, subst)
	except Exception as e:
		print(e)
		frappe.log_error(e, "Frappe Files Modifications")

	# Different File
	frappe_file = frappe.get_app_path("frappe", "utils", "setup_docs.py")

	pattern = 'self.add_sidebars()'
	subst = ''
	try:
		replace(frappe_file, pattern, subst)
	except Exception as e:
		print(e)
		frappe.log_error(e, "Frappe Files Modifications")

	# Different File
	frappe_file = frappe.get_app_path("frappe", "database.py")

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

def remove_erpnext_footer():
	erpnex_footer_folder = frappe.get_app_path("erpnext", "templates", "includes", "footer")
	try:
		if os.path.exists(erpnex_footer_folder):
			rmtree(erpnex_footer_folder)
	except Exception as e:
		print(e)
		frappe.log_error(e, "ERPNext Footer Deletion")

def change_log_removal():
	users = frappe.get_all("User")

	for user in users:
		last_know_versions = frappe.db.get_value("User", user.name, "last_known_versions")

		if last_know_versions is not None:
			versions = json.loads(last_know_versions)

			versions['erpnext']['version'] = frappe.get_attr("erpnext.__version__")
			versions['frappe']['version'] = frappe.get_attr("frappe.__version__")

			frappe.db.set_value("User", user, "last_known_versions", json.dumps(versions), update_modified=False)


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
	remove_deletion_from_permissions()
	prevent_company_reset()
	delete_standard_config_files()
	delete_erpnext_hooks()
	delete_frappe_hooks()
	modify_frappe_files()
	remove_erpnext_footer()
	change_log_removal()
