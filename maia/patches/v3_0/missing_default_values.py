from __future__ import unicode_literals
import frappe
from maia.setup.setup_wizard.operations.maia_setup import set_default_print_formats
from frappe.utils.user import get_system_managers

def execute():
	pics = frappe.get_all("Professional Information Card")
	for pic in pics:
		frappe.db.set_value("Professional Information Card", pic.name, "social_security_rate", "Normal Rate (70%)")

	set_default_print_formats()

	system_manager = get_system_managers(only_name=True)

	if not frappe.db.get_value("Contact Us Settings", None, "forward_to_email"):
		frappe.db.set_value("Contact Us Settings", None, "forward_to_email", system_manager[0])

