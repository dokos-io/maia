# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
import maia
from six import string_types

def execute():
	frappe.reload_doc("maia", "doctype", "Drug Prescription")
	for consult in maia.get_consultation_types():
		docs = frappe.get_all(consult, fields=["cpam_share_display", "name", "overpayment_value", "codification_value", "without_codification_display"])

		for doc in docs:
			if doc.cpam_share_display and not isinstance(doc.cpam_share_display, float) and len(doc.cpam_share_display.split("€")) > 1:
				frappe.db.set_value(consult, doc.name, "cpam_share_display", doc.cpam_share_display.split("€")[1].replace(",", "."), update_modified=False)
			elif not doc.cpam_share_display:
				frappe.db.set_value(consult, doc.name, "cpam_share_display", 0)

			if doc.without_codification_display and not isinstance(doc.without_codification_display, float) and len(doc.without_codification_display.split("€")) > 1:
				frappe.db.set_value(consult, doc.name, "without_codification_display", doc.without_codification_display.split("€")[1].replace(",", "."), update_modified=False)
			elif not doc.without_codification_display:
				frappe.db.set_value(consult, doc.name, "without_codification_display", 0)

		frappe.db.commit()

		frappe.reload_doc("maia", "doctype", consult)
		docs = frappe.get_all(consult)

		for d in docs:
			consultation = frappe.get_doc(consult, d.name)

			allowances = 0

			allowances += consultation.night_work_allowance_value
			allowances += consultation.sundays_holidays_allowance_value
			allowances += consultation.lump_sum_travel_allowance_value
			allowances += consultation.mileage_allowance_value

			frappe.db.set_value(consult, d.name, "total_allowances", allowances, update_modified=False)
