# Copyright (c) 2018, DOKOS and Contributors

import frappe
import shutil


def add_simplified_coa():
	french_coa = frappe.get_app_path("maia", "customizations", "chart_of_accounts", "fr_plan_comptable_general.json")
	verified_folder = frappe.get_app_path("erpnext", "accounts", "doctype", "account", "chart_of_accounts", "verified")
	try:
		shutil.copy(french_coa, verified_folder)
	except Exception as e:
		print(e)
		frappe.log_error(e, "CoA Error")
