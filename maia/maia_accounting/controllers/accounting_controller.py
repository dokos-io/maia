# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
from maia.maia_accounting.controllers.status_updater import StatusUpdater
from maia.maia_accounting.doctype.general_ledger_entry.general_ledger_entry import make_gl_entries

class AccountingController(StatusUpdater):
	def set_outstanding_amount(self):
		self.outstanding_amount = self.amount
		self.set_status()
	
	def reverse_gl_entries(self):
		gl_entries = frappe.get_all("General Ledger Entry", filters={"link_doctype": self.doctype, \
			"link_docname": self.name})

		cancellation_entries = []
		for entry in gl_entries:
			gl = frappe.get_doc("General Ledger Entry", entry.name)
			cancellation_entries.append({
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
				"party": gl.party,
				"practitioner": gl.practitioner
			})

		make_gl_entries(cancellation_entries, ignore_links=True)