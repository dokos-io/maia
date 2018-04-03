# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.accounts.party import get_party_account
from frappe.utils import flt
from frappe import _
from erpnext.accounts.doctype.journal_entry.journal_entry import get_default_bank_cash_account


class MealExpense(Document):
	def validate(self):
		pass

	def on_submit(self):
		self.make_journal_entry()

	def on_cancel(self):
		pe = frappe.get_doc("Journal Entry", self.payment_entry)
		pe.cancel()

		jv = frappe.get_doc("Journal Entry", self.journal_entry)
		jv.cancel()

	def on_trash(self):
		pe = frappe.get_doc("Journal Entry", self.payment_entry)
		pe.delete()

		jv = frappe.get_doc("Journal Entry", self.journal_entry)
		jv.delete()

	def make_journal_entry(self):
		jv = frappe.new_doc("Journal Entry")
		jv.title = self.supplier + " - " + _("Meal Expense")
		jv.posting_date = self.posting_date
		jv.company = self.company
		jv.user_remark = self.remarks

		supplier_account = get_party_account("Supplier", self.supplier, self.company)
		bank_account = get_default_bank_cash_account(self.company, "Bank", mode_of_payment=self.mode_of_payment)

		jv.set("accounts", [
			{
				"account": self.meal_expense_deductible_account,
				"debit_in_account_currency": abs(flt(self.deductible_share)),
				"credit_in_account_currency": 0,
			},
			{
				"account": self.meal_expense_non_deductible_account,
				"debit_in_account_currency": abs(flt(self.non_deductible_share)),
				"credit_in_account_currency": 0,
			},
			{
				"account": supplier_account,
				"party_type": "Supplier",
				"party": self.supplier,
				"is_advance": "No",
				"credit_in_account_currency": abs(flt(self.meal_amount)),
				"debit_in_account_currency": 0,
			}
		])
		jv.insert()
		jv.submit()

		frappe.db.set_value(self.doctype, self.name, "journal_entry", jv.name)

		self.make_payment_entry(jv.name)

	def make_payment_entry(self, journal_entry_name):
		pe = frappe.new_doc("Journal Entry")
		pe.title = self.supplier + " - " + _("Meal Expense Payment")
		pe.posting_date = self.posting_date
		pe.company = self.company
		pe.user_remark = self.remarks

		supplier_account = get_party_account("Supplier", self.supplier, self.company)
		bank_account = get_default_bank_cash_account(self.company, "Bank", mode_of_payment=self.mode_of_payment)

		frappe.logger().debug(self.journal_entry)

		pe.set("accounts", [
			{
				"account": bank_account.account,
				"debit_in_account_currency": 0,
				"credit_in_account_currency": abs(flt(self.meal_amount)),
			},
			{
				"account": supplier_account,
				"party_type": "Supplier",
				"party": self.supplier,
				"is_advance": "No",
				"reference_type": "Journal Entry",
				"reference_name": journal_entry_name,
				"credit_in_account_currency": 0,
				"debit_in_account_currency": abs(flt(self.meal_amount)),
			}
		])
		pe.insert()
		pe.submit()

		frappe.db.set_value(self.doctype, self.name, "payment_entry", pe.name)
