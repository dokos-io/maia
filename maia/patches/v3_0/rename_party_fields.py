from __future__ import unicode_literals
import frappe
from frappe.model.utils.rename_field import rename_field

def execute():
	frappe.reload_doc('maia_accounting', 'doctype', 'party')

	rename_field("Party", "is_customer", "allow_revenues")
	rename_field("Party", "is_supplier", "allow_expenses")

