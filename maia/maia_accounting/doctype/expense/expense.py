# -*- coding: utf-8 -*-
# Copyright (c) 2019, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from maia.maia_accounting.controllers.accounting_controller import AccountingController
from frappe.utils import flt
from frappe import _
from maia.maia_accounting.utils import get_accounting_query_conditions

class Expense(AccountingController):
	def validate(self):
		self.set_outstanding_amount()
		self.set_status()
		self.validate_fields()

		if self.reference_doctype == "Maia Asset" and self.reference_name:
			if frappe.db.get_value(self.reference_doctype, self.reference_name, "expense") != self.name:
				frappe.db.set_value(self.reference_doctype, self.reference_name, "expense", self.name)

	def before_submit(self):
		self.set_outstanding_amount()

	def on_submit(self):
		self.set_status()

	def on_cancel(self):
		if self.reference_doctype == "Maia Asset" and frappe.db.get_value(self.reference_doctype, self.reference_name, "expense") == self.name:
				frappe.db.set_value(self.reference_doctype, self.reference_name, "expense", None)

	def validate_fields(self):
		if self.expense_type == "Personal debit":
			self.party = None

@frappe.whitelist()	
def register_personal_debit(docname, payment_method):
	doc =  frappe.get_doc("Expense", docname)

	pay = frappe.get_doc({
		"doctype": "Payment",
		"payment_date": doc.transaction_date,
		"practitioner": doc.practitioner,
		"payment_type": "Outgoing payment",
		"paid_amount": doc.amount,
		"payment_method": payment_method,
		"payment_references": [
			{
			"reference_type": doc.doctype,
			"reference_name": doc.name,
			"outstanding_amount": doc.outstanding_amount,
			"paid_amount": doc.amount
			}
		]
	})

	pay.insert()
	pay.submit()

	return pay.name

@frappe.whitelist()
def get_asset_expense(dt, dn):
	asset = frappe.get_doc(dt, dn)

	asset_purchasing_item = frappe.db.get_value("Accounting Item", dict(accounting_item_type="Asset Purchasing"), "name")

	expense = frappe.new_doc("Expense")
	expense.label = asset.asset_label
	expense.expense_type = "Miscellaneous"
	expense.amount = asset.asset_value
	expense.accounting_item = asset_purchasing_item
	expense.reference_doctype = dt
	expense.reference_name = dn

	if flt(asset.deduction_ceiling) < flt(asset.asset_value):
		expense.with_items = 1

		expense.append("expense_items",
			{
				"label": _("Deductible amount"),
				"accounting_item": asset_purchasing_item,
				"total_amount": asset.deduction_ceiling
			}
		)
		expense.append("expense_items",
			{
				"label": _("Non-deductible amount"),
				"accounting_item": frappe.db.get_value("Accounting Item", dict(accounting_item_type="Practitioner"), "name"),
				"total_amount": (flt(asset.asset_value) - flt(asset.deduction_ceiling))
			}
		)

	return expense

def get_permission_query_conditions(user):
	return get_accounting_query_conditions("Expense", user)