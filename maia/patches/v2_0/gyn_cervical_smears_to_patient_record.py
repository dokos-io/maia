# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe


def execute():
	cervical_smears = frappe.get_all("Cervical Smear")

	for cervical_smear in cervical_smears:
		doc = frappe.get_doc("Cervical Smear", cervical_smear.name)
		if doc.parenttype != "Patient Record":
			patient_record = frappe.get_value(doc.parenttype, doc.parent, "patient_record")

			try:
				frappe.db.sql("""update `tabCervical Smear` set parenttype='Patient Record', parent='{0}', parentfield='cervical_smear_table' where name='{1}'""".format(patient_record, doc.name))
			except Exception as e:
				print(e)
