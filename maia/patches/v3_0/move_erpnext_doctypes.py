# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe

def execute():
	frappe.reload_doc('maia', 'doctype', 'profession')
	frappe.reload_doc('maia', 'doctype', 'employment_status')

	designations = frappe.get_all("Designation", fields=["*"])

	for designation in designations:
		prof = frappe.new_doc("Profession")
		prof.profession = designation["description"]
		prof.profession_name = designation["designation_name"]
		try:
			prof.insert(ignore_permissions=True)
		except frappe.DuplicateEntryError as e:
			print(e)

	emp_types = frappe.get_all("Employment Type", fields=["*"])

	for emp_type in emp_types:
		emp_status = frappe.new_doc("Employment Status")
		emp_status.employee_type_name = emp_type["employee_type_name"]
		try:
			emp_status.insert(ignore_permissions=True)
		except frappe.DuplicateEntryError as e:
			print(e)