# Copyright (c) 2019, Dokos and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from maia.maia_accounting.controllers.status_updater import StatusUpdater

class AccountingController(StatusUpdater):
	def set_outstanding_amount(self):
		self.outstanding_amount = self.amount
	
	def reverse_gl_entries(self):
		gl_entries = frappe.get_all("General Ledger Entry", filters={"link_doctype": self.doctype, \
			"link_docname": self.name})

		cancelation_entries = []
		for entry in gl_entries:
			gl = frappe.get_doc("General Ledger Entry", entry.name)
			cancelation_entries.append({
				"posting_date": gl.posting_date,
				"accounting_item": gl.accounting_item,
				"debit": gl.credit,
				"credit": gl.debit,
				"currency": gl.currency,
				"reference_type": gl.reference_type,
				"reference_name": gl.reference_name,
				"link_doctype": gl.link_doctype,
				"link_docname": gl.link_docname,
				"accounting_journal": gl.accounting_journal,
				"practitioner": gl.practitioner
			})

		make_gl_entries(cancelation_entries)