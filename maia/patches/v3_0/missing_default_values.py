from __future__ import unicode_literals
import frappe
from maia.setup.setup_wizard.operations.maia_setup import set_default_print_formats

def execute():
	pics = frappe.get_all("Professional Information Card")
	for pic in pics:
		frappe.db.set_value("Professional Information Card", pic.name, "social_security_rate", "Normal Rate (70%)")

	set_default_print_formats()
