# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import add_days, getdate

def execute():
	credit_notes = frappe.get_all("Sales Invoice", filters={"is_return": 1})

	for credit_note in credit_notes:
		doc = frappe.get_doc("Sales Invoice", credit_note.name)

		if doc.return_against:
			date = frappe.db.get_value("Sales Invoice", doc.return_against, "posting_date")

			if date != doc.posting_date:
				frappe.db.set_value("Sales Invoice", doc.name, "posting_date", date, update_modified=False)

				gl_entries = frappe.get_all("GL Entry", filters={"voucher_type": "Sales Invoice", "voucher_no": doc.name})

				for gl in gl_entries:
					frappe.db.set_value("GL Entry", gl.name, "posting_date", date, update_modified=False)

	
	payments = frappe.get_all("Payment Entry")

	for payment in payments:
		doc = frappe.get_doc("Payment Entry", payment.name)

		if len(doc.references) == 1 and getdate(doc.posting_date) > getdate(add_days(doc.reference_date, 90)):
			frappe.db.set_value("Payment Entry", doc.name, "posting_date", doc.reference_date, update_modified=False)

			gl_entries = frappe.get_all("GL Entry", filters={"voucher_type": "Payment Entry", "voucher_no": doc.name})

			for gl in gl_entries:
				frappe.db.set_value("GL Entry", gl.name, "posting_date", doc.reference_date, update_modified=False)

	
