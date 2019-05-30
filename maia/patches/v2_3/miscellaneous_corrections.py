# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute():
	try:
		frappe.rename_doc('Item', 'Clothing Expenses', 'Dépenses Vestimentaires')
	except Exception as e:
		print(e)
	try:
		frappe.rename_doc('Item', 'Office Furniture', 'Fournitures de Bureau')
	except Exception as e:
		print(e)
	try:
		frappe.rename_doc('Item', 'Laundering Expenses', 'Frais de Blanchiment')
	except Exception as e:
		print(e)


	companies = frappe.get_all("Company")

	for company in companies:
		abbr = frappe.get_value("Company", company.name, "abbr")
		try:
			existing_account = frappe.get_doc("Account", "6257 - Frais de réceptions déductibles - " + abbr)

		except:
			child_account = frappe.get_doc({
				"doctype": "Account",
				"root_type": "Expense",
				"company": company.name,
				"parent_account": "625 - Déplacements, missions et réceptions - " + abbr,
				"account_name": "Frais de réceptions",
				"account_number": "6257",
				"account_type": "Expense Account",
				"is_group": 1})

			try:
				child_account.insert(ignore_permissions=True)
				frappe.db.commit()
			except Exception as e:
				print(e)
				pass


		try:
			acc = frappe.get_doc('Account', '625700 - Frais de réceptions déductibles - ' + abbr)
			acc.parent_account = "6257 - Frais de réceptions - " + abbr
			acc.save()
		except Exception as e:
			print(e)
			pass

		try:
			acc = frappe.get_doc('Account', '625710 - Frais de réceptions non déductibles - ' + abbr)
			acc.parent_account = "6257 - Frais de réceptions - " + abbr
			acc.save()
		except Exception as e:
			print(e)
			pass


		try:
			frappe.rename_doc('Account', '625700 - Frais de réceptions déductibles - ' + abbr, '625700 - Frais de repas déductibles')
		except Exception as e:
			print(e)
			pass


		second_child_account = frappe.get_doc({
			"doctype": "Account",
			"root_type": "Expense",
			"company": company.name,
			"parent_account": "6257 - Frais de réceptions - " + abbr,
			"account_name": "Frais de réceptions déductibles",
			"account_number": "625720",
			"account_type": "Expense Account",
			"is_group": 0})

		try:
			second_child_account.insert(ignore_permissions=True)
			frappe.db.commit()
		except Exception as e:
			print(e)
			pass

		language = frappe.get_single("System Settings").language
		frappe.local.lang = language

		if frappe.db.exists("Item", "Office Supplies"):
			item = frappe.get_doc("Item", "Office Supplies")
			item.item_group = _('Office Supplies, Documentation, Post Office')
			item.save()
