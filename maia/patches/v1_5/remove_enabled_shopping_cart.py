from __future__ import unicode_literals
import frappe


def execute():
	settings = frappe.get_doc("Shopping Cart Settings")
	settings.enabled = 0
	settings.save()
	frappe.db.commit()
