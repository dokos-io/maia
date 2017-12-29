# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _

def execute():
	companies = frappe.get_all("Company")

	for company in companies:
		abbr = frappe.get_value("Company", company.name, "abbr")

		try:
			account_625 = frappe.get_doc("Account", "625-Déplacements, missions et réceptions - " + abbr)
			if account_625.is_group == 1:
				print("Account 625 is a Group")
			else:
				try:
					frappe.rename_doc("Account", "625-Déplacements, missions et réceptions - " + abbr, "625700-Frais de réceptions déductibles - " + abbr)
					frappe.db.commit()
				except Exception as e:
					print(e)
		except Exception as e:
			print(e)

		try:
			parent_account = frappe.get_doc({
				"doctype": "Account",
				"root_type": "Expense",
				"company": company.name,
				"parent_account": "62-Autres services extérieurs - " + abbr,
				"account_name": "625-Déplacements, missions et réceptions",
				"is_group": 1})

			parent_account.insert(ignore_permissions=True)
		except Exception as e:
			print(e)

		try:
			child_account = frappe.get_doc({
				"doctype": "Account",
				"root_type": "Expense",
				"company": company.name,
				"parent_account": "625-Déplacements, missions et réceptions - " + abbr,
				"account_name": "625100-Voyages et déplacements",
				"account_type": "Expense Account",
				"is_group": 0})

			child_account.insert(ignore_permissions=True)
		except Exception as e:
			print(e)

		try:
			frappe.db.set_value("Item Group", _("Other Travel Related Costs"), "default_expense_account", "625100-Voyages et déplacements - " + abbr)
		except Exception as e:
			print(e)

		try:
			deductible_account = frappe.get_doc("Account", "625700-Frais de réceptions déductibles - " + abbr)
			deductible_account.parent_account = "625-Déplacements, missions et réceptions - " + abbr
			deductible_account.save()
		except Exception as e:
			print(e)

		frappe.db.commit()
