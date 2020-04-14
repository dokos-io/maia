# -*- coding: utf-8 -*-
# Copyright (c) 2019, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt

from maia.maia_accounting.utils import get_balance_on

REVENUE = ["Revenue", "Asset Selling", "Sales Party"]
EXPENSE = ["Expense", "Meal", "Travel", "Social contributions", "Asset purchasing", "Asset depreciation charge", "Purchase Party"]

class AccountingItem(Document):
	def is_revenue_item(self):
		return self.accounting_item_type in REVENUE

	def is_expense_item(self):
		return self.accounting_item_type in EXPENSE


def get_accounts(acc_type):
	fields = ["name", "accounting_item_type", "accounting_number", "accounting_journal"]
	if acc_type == "Revenue":
		return frappe.get_all("Accounting Item", filters={"accounting_item_type": ["in", REVENUE]}, fields=fields)
	elif acc_type == "Expense":
		return frappe.get_all("Accounting Item", filters={"accounting_item_type": ["in", EXPENSE]}, fields=fields)
	elif acc_type == "Practitioner":
		return frappe.get_all("Accounting Item", filters={"accounting_item_type": "Practitioner"}, fields=fields)

def get_revenue(date, practitioner):
	revenue_items = frappe.get_all("Accounting Item", filters={"accounting_item_type": ["in", REVENUE]})
	revenue = 0

	for item in revenue_items:
		revenue += get_balance_on(account= item.name, date=date, practitioner=practitioner)

	return abs(revenue)

def get_expenses(date, practitioner):
	expense_items = frappe.get_all("Accounting Item", filters={"accounting_item_type": ["in", EXPENSE]})
	expense = 0

	for item in expense_items:
		expense += get_balance_on(account= item.name, date=date, practitioner=practitioner)

	return abs(expense)

def get_profit_loss(date, practitioner):
	revenue = get_revenue(date, practitioner)
	expense = get_expenses(date, practitioner)

	return flt(revenue) - flt(expense)