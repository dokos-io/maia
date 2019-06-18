from __future__ import unicode_literals
import frappe

def execute():
	pics = frappe.get_all("Professional Information Card")
	for pic in pics:
		frappe.db.set_value("Professional Information Card", pic.name, "social_security_rate", "Normal Rate (70%)")
