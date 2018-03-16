# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe


def execute():
	correspondents = frappe.get_all("Correspondents")
	print(len(correspondents))

	for correspondent in correspondents:
		doc = frappe.get_doc("Correspondents", correspondent.name)
		patient_record = frappe.get_value(doc.parenttype, doc.parent, "patient_record")

		try:
			frappe.db.sql("""update `tabCorrespondents` set parenttype='Patient Record', parent='{0}' where name='{1}'""".format(patient_record, doc.name))
		except Exception as e:
			print(e)
