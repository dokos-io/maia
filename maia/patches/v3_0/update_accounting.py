# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
import maia
from six import string_types

def execute():
	for consult in maia.get_consultation_types():
		docs = frappe.get_all(consult, fields=["cpam_share_display", "name", "overpayment_value", "codification_value", "without_codification_display"])

		for doc in docs:
			if doc.cpam_share_display and not isinstance(doc.cpam_share_display, float):
				frappe.db.set_value(consult, doc.name, "cpam_share_display", doc.cpam_share_display.split("€")[1].replace(",", "."), update_modified=False)
			else:
				frappe.db.set_value(consult, doc.name, "cpam_share_display", 0, update_modified=False)

			if doc.overpayment_value and not isinstance(doc.overpayment_value, float):
				frappe.db.set_value(consult, doc.name, "overpayment_value", doc.overpayment_value.split("€")[1].replace(",", "."), update_modified=False)
			else:
				frappe.db.set_value(consult, doc.name, "overpayment_value", 0, update_modified=False)

			if doc.codification_value and not isinstance(doc.codification_value, string_types):
				frappe.db.set_value(consult, doc.name, "codification_value", doc.codification_value.split("€")[1].replace(",", "."), update_modified=False)
			else:
				frappe.db.set_value(consult, doc.name, "codification_value", 0, update_modified=False)

			if doc.without_codification_display:
				frappe.db.set_value(consult, doc.name, "without_codification_display", doc.without_codification_display.split("€")[1].replace(",", "."), update_modified=False)
			else:
				frappe.db.set_value(consult, doc.name, "without_codification_display", 0, update_modified=False)

		for doc in docs:
			consultation = frappe.get_doc(consult, doc.name)

			allowances = 0

			allowances += consultation.night_work_allowance_value
			allowances += consultation.sundays_holidays_allowance_value
			allowances += consultation.lump_sum_travel_allowance_value
			allowances += consultation.mileage_allowance_value

			frappe.db.set_value(consult, doc.name, "total_allowances", allowances, update_modified=False)
