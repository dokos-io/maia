# -*- coding: utf-8 -*-
# Copyright (c) 2019, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from maia.maia_accounting.controllers.accounting_controller import AccountingController

class Expense(AccountingController):
	def validate(self):
		self.set_status()

	def before_submit(self):
		self.set_outstanding_amount()

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

	expense = frappe.new_doc("Expense")
	expense.label = asset.asset_label
	expense.expense_type = "Miscellaneous"
	expense.amount = asset.asset_value
	expense.accounting_item = frappe.db.get_value("Accounting Item", dict(accounting_item_type="Asset Purchasing"), "name")

	return expense