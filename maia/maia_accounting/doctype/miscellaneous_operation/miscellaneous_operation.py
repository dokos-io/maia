# -*- coding: utf-8 -*-
# Copyright (c) 2019, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt, add_years, getdate
from maia.maia_accounting.controllers.accounting_controller import AccountingController
from maia.maia_accounting.doctype.general_ledger_entry.general_ledger_entry import make_gl_entries
from maia.maia_accounting.utils import get_accounting_query_conditions
from maia.maia_accounting.doctype.payment.payment import update_clearance_date
import json
from maia.maia_accounting.doctype.accounting_item.accounting_item import get_accounts
from maia.maia_accounting.report.maia_general_ledger.maia_general_ledger import get_opening_balance
from maia.maia_accounting.report.trial_balance.trial_balance import get_period_movements, get_closing_balance
from collections import defaultdict
from maia.maia_accounting.utils import get_fiscal_year

class MiscellaneousOperation(AccountingController):
	def validate(self):
		if not self.title:
			self.title = _(self.operation_type)
		self.check_journals()

	def on_submit(self):
		if self.operation_type == "Annual Closing":
			self.make_closing_voucher()
		else:
			self.check_journals()
			self.check_difference()
			self.make_gl_entries()

	def on_cancel(self):
		self.reverse_gl_entries()
		self.flags.ignore_links = True

	def on_trash(self):
		frappe.throw(_("Deleting this document is not permitted."))

	def check_journals(self):
		journals = [x.accounting_journal for x in self.items]

		if set(["Sales", "Purchases"]).issubset(journals):
			frappe.throw(_("Making a miscellaneous operation between a sales and a purchase item is not authorized"))

		if self.operation_type not in ["Fee Retrocession"]:
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
			if flt(item.amount) == 0:
				continue

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
				"accounting_journal": item.accounting_journal, # if self.operation_type in ["Internal Transfer"] else "Miscellaneous operations",
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

	def make_closing_voucher(self):
		fiscal_year = get_fiscal_year(date=self.posting_date, practitioner=self.practitioner)
		journal = frappe.db.get_value("Accounting Item", self.profit_loss, "accounting_journal")

		gl_entries = []
		total = 0
		for account_type in ("Revenue", "Expense", "Practitioner"):
			accounts = get_accounts(account_type)

			for account in accounts:
				filters = { "practitioner": self.practitioner, "accounting_item": account.name, "from_date": fiscal_year[1], "to_date": fiscal_year[2] }
				balance = self.get_balance(filters)

				if balance.get("debit") or balance.get("credit"):
					amount = flt(balance.get("debit")) - flt(balance.get("credit"))
					total += amount
					gl_entries.append({
						"posting_date": self.posting_date,
						"accounting_item": account.name,
						"debit": flt(amount) if amount > 0 else 0,
						"credit": abs(flt(amount)) if amount < 0 else 0,
						"currency": "EUR",
						"reference_type": self.doctype,
						"reference_name": self.name,
						"link_doctype": self.doctype,
						"link_docname": self.name,
						"accounting_journal": journal,
						"party": None,
						"practitioner": self.practitioner
					})

		make_gl_entries(gl_entries)

	@staticmethod
	def get_balance(filters):
		opening_balance = get_opening_balance(filters.get("from_date"), filters)
		period_movements = get_period_movements(filters)
		return get_closing_balance(opening_balance, period_movements)

@frappe.whitelist()
def update_clearance_dates(documents, date):
	documents = json.loads(documents)
	for document in documents:
		update_clearance_date(document["payment"], date)

def get_permission_query_conditions(user):
	return get_accounting_query_conditions("Miscellaneous Operation", user)

@frappe.whitelist()
def get_closing_date(date, practitioner):
	return get_fiscal_year(date=add_years(getdate(date), -1), practitioner=practitioner)
