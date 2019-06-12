# -*- coding: utf-8 -*-
# Copyright (c) 2019, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt
from maia.maia_accounting.controllers.accounting_controller import AccountingController
from maia.maia_accounting.doctype.general_ledger_entry.general_ledger_entry import make_gl_entries
from maia.maia_accounting.utils import get_accounting_query_conditions

class MiscellaneousOperation(AccountingController):
	def validate(self):
		self.check_journals()

	def on_submit(self):
		self.check_journals()
		self.check_difference()
		self.make_gl_entries()

	def on_cancel(self):
		self.reverse_gl_entries()

	def check_journals(self):
		journals = [x.accounting_journal for x in self.items]

		if set(["Sales", "Purchases"]).issubset(journals):
			frappe.throw(_("Making a miscellaneous operation between a sales and a purchase item is not authorized"))

		if set(["Sales", "Bank"]).issubset(journals) or set(["Sales", "Cash"]).issubset(journals):
			frappe.throw(_("Making a payment is not authorized in the miscellaneous operations. Please use the Revenue document or make an internal transfer."))

		if set(["Purchases", "Bank"]).issubset(journals) or set(["Purchases", "Cash"]).issubset(journals):
			frappe.throw(_("Making a payment is not authorized in the miscellaneous operations. Please use the Expense document or make an internal transfer."))

	def check_difference(self):
		if flt(self.difference) != 0:
			frappe.throw(_("The difference between positive and negative amounts must be equal to 0"))

	def make_gl_entries(self):
		gl_entries = []
		for item in self.items:
			if not item.accounting_journal:
				item.accounting_journal = frappe.db.get_value("Accounting Item", item.accounting_item, "accounting_journal")
			if item.accounting_journal in ["Sales"]:
				debit = abs(flt(item.amount)) if flt(item.amount) < 0 else 0
				credit = flt(item.amount) if flt(item.amount) > 0 else 0
			elif item.accounting_journal in ["Purchases", "Cash", "Bank", "Miscellaneous operations"]:
				debit = flt(item.amount) if flt(item.amount) > 0 else 0
				credit = abs(flt(item.amount)) if flt(item.amount) < 0 else 0

			gl_entries.append({
				"posting_date": self.posting_date,
				"accounting_item": item.accounting_item,
				"debit": debit,
				"credit": credit,
				"currency": "EUR",
				"reference_type": self.doctype,
				"reference_name": self.name,
				"link_doctype": self.doctype,
				"link_docname": self.name,
				"accounting_journal": item.accounting_journal if self.operation_type in ["Internal Transfer"] else "Miscellaneous operations",
				"party": None,
				"practitioner": self.practitioner
			})

			if self.operation_type in ["Internal Transfer", "Opening Entry"]:
				internal_transfer_account = frappe.get_doc("Accounting Item", dict(accounting_item_type="Internal transfer")) \
					if self.operation_type == "Internal Transfer" \
					else frappe.get_doc("Accounting Item", dict(accounting_item_type="Opening"))

				gl_entries.append({
					"posting_date": self.posting_date,
					"accounting_item": internal_transfer_account.accounting_item,
					"debit": credit,
					"credit": debit,
					"currency": "EUR",
					"reference_type": self.doctype,
					"reference_name": self.name,
					"link_doctype": self.doctype,
					"link_docname": self.name,
					"accounting_journal": item.accounting_journal,
					"party": None,
					"practitioner": self.practitioner
				})

		make_gl_entries(gl_entries)

def get_permission_query_conditions(user):
	return get_accounting_query_conditions("Miscellaneous Operation", user)