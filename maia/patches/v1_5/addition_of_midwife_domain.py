# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe


def execute():
	doc = frappe.new_doc("Domain")
	doc.domain = "Sage-Femme"
	try:
		doc.insert(ignore_permissions=True)
		frappe.db.commit()
	except Exception as e:
		print(e)

	# Reset company customization to default
	frappe.db.sql("""delete from `tabProperty Setter` where doc_type=%s
			and ifnull(field_name, '')!='naming_series'""", "Company")
	frappe.clear_cache(doctype="Company")
