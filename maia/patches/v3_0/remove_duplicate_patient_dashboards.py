# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe

def execute():
	dashboards = frappe.db.sql("""
		select patient_record, count(patient_record)
		from `tabCustom Patient Record Dashboard`
		group by patient_record
		having count(patient_record) > 1
		""", as_dict=True)

	for dashboard in dashboards:
		items = frappe.get_all("Custom Patient Record Dashboard", filters={"patient_record": dashboard.patient_record}, order_by="creation desc")

		count = 0
		for item in items:
			if count == 0:
				count += 1
				continue
			else:
				count += 1
				frappe.delete_doc("Custom Patient Record Dashboard", item.name)

	frappe.db.commit()