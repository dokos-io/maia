from __future__ import unicode_literals
import frappe


def execute():
	doc = frappe.get_doc("Shopping Cart Settings", None)
	doc.enabled = 0
	doc.save()

	doc = frappe.get_doc("Role", "Guest")
	doc.desk_access = 0
	doc.save()

	frappe.db.commit()
