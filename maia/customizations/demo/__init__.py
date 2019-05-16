# Copyright (c) 2018, DOKOS and Contributors

import frappe
import shutil

def add_demo_page():
	return
	#TODO: rewrite demo
	maia_demo = frappe.get_app_path("maia", "customizations", "demo", "demo.html")
	erpnext_folder = frappe.get_app_path("erpnext", "templates", "pages")
	try:
		shutil.copy(maia_demo, erpnext_folder)
	except Exception as e:
		print(e)
		frappe.log_error(e, "Demo Error")
