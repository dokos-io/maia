# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute():
	companies = frappe.get_all("Company")

	for company in companies:
		abbr = frappe.get_value("Company", company.name, "abbr")
		try:
			account = frappe.get_doc("Account", "431 - Sécurité Sociale - " + abbr)
			account.account_type = "Payable"
			account.save()
			frappe.db.commit()
		except Exception as e:
			print(e)

		try:
			account = frappe.get_doc("Account", "437 - Autres organismes sociaux - " + abbr)
			account.account_type = "Payable"
			account.save()
			frappe.db.commit()
		except Exception as e:
			print(e)


	st = frappe.get_doc({
		'doctype': 'Supplier Type',
		'supplier_type': 'Sécurité Sociale',
	})
	try:
		st.insert(ignore_permissions=True)
	except frappe.DuplicateEntryError as e:
		pass

	for company in companies:
		abbr = frappe.get_value("Company", company.name, "abbr")
		st = frappe.get_doc("Supplier Type", 'Sécurité Sociale')

		st.append("accounts", {
			"company": company.name,
			"account": ("431 - Sécurité sociale - " + abbr)
		})
		st.save()

	if not frappe.db.exists("Supplier", 'URSSAF'):
		ss = frappe.get_doc({
			'doctype': 'Supplier',
			'supplier_name': 'URSSAF',
			'supplier_type': 'Sécurité Sociale'
		})
		ss.insert(ignore_permissions=True)

	language = frappe.get_single("System Settings").language
	frappe.local.lang = language

	records = [
	{'doctype': 'Item', 'item_code': _('Family Allowances'), 'item_name': _('Family Allowances'), 'item_group': _('Personal Social Security Contributions'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
	{'doctype': 'Item', 'item_code': _('Health Insurance'), 'item_name': _('Health Insurance'), 'item_group': _('Personal Social Security Contributions'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
	{'doctype': 'Item', 'item_code': _('Contribution to vocational training'), 'item_name': _('Contribution to vocational training'), 'item_group': _('Personal Social Security Contributions'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
	{'doctype': 'Item', 'item_code': _('CURPS'), 'item_name': _('CURPS'), 'item_group': _('Personal Social Security Contributions'), 'stock_uom': _('Unit'), 'is_purchase_item': 1, 'is_sales_item': 0, 'publish_in_hub': 0},
	]

	from frappe.modules import scrub
	for r in records:
		print(r)
		doc = frappe.new_doc(r.get("doctype"))
		doc.update(r)

		# ignore mandatory for root
		parent_link_field = ("parent_" + scrub(doc.doctype))
		if doc.meta.get_field(parent_link_field) and not doc.get(parent_link_field):
			doc.flags.ignore_mandatory = True

		try:
			doc.insert(ignore_permissions=True)
		except frappe.DuplicateEntryError as e:
			# pass DuplicateEntryError and continue
			if e.args and e.args[0]==doc.doctype and e.args[1]==doc.name:
				# make sure DuplicateEntryError is for the exact same doc and not a related doc
				pass
			else:
				raise
