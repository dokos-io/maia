# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe

def execute():
	frappe.db.set_value("Default Template", "Default Template", "button_link", "/appointment")
	frappe.get_doc("Default Template", "Default Template").build_new_theme()

	#Delete links in files
	doctypes = [x["name"] for x in frappe.get_all("DocType")]
	files = frappe.get_all("File", fields=["name", "attached_to_doctype"])

	for file in files:
		if file.attached_to_doctype not in doctypes:
			frappe.db.set_value("File", file.name, "attached_to_doctype", None)
			frappe.db.set_value("File", file.name, "attached_to_name", None)