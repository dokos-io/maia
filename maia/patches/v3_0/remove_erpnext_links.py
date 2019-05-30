# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
from frappe.installer import remove_app

def execute():
	frappe.delete_doc("Dashboard Chart Source", "Account Balance Timeline")

	erpnext_modules = ["Selling", "Accounts", "Assets", "Buying", \
		"HR", "Maintenance", "Manufacturing", "Quality Management", "Regional", "Stock", "Support"]

	notifications = frappe.get_all("Notification")
	for notification in notifications:
		frappe.delete_doc("Notification", notification.name)

	print_formats = frappe.get_all("Print Format", filters={"module": ["in", erpnext_modules]})

	for print_format in print_formats:
		frappe.delete_doc("Print Format", print_format.name)

	data_migration_plans = frappe.get_all("Data Migration Plan")

	for data_migration_plan in data_migration_plans:
		frappe.delete_doc("Data Migration Plan", data_migration_plan.name)

	erpnext_doctypes = [x["name"] for x in frappe.get_all("DocType", filters={"module": ["in", erpnext_modules]})]

	custom_fields = frappe.get_all("Custom Field", filters={"options": ["in", erpnext_doctypes], "fieldtype": "Link"})
	for custom_field in custom_fields:
		frappe.delete_doc("Custom Field", custom_field.name)

	property_setters = frappe.get_all("Property Setter", filters={"doc_type": ["in", erpnext_doctypes]})
	for property_setter in property_setters:
		frappe.delete_doc("Property Setter", property_setter.name)
	
	print_formats = frappe.get_all("Print Format", filters={"doc_type": ["in", erpnext_doctypes]})
	for print_format in print_formats:
		frappe.delete_doc("Print Format", print_format.name)

	# Add Quittance Maia
	print_format = frappe.get_doc("Print Format", "Quittance Maia")
	frappe.make_property_setter({
		'doctype_or_field': "DocType",
		'doctype': print_format.doc_type,
		'property': "default_print_format",
		'value': name,
	})

	# Move home page to new web page
	tag_line = frappe.db.get_value("Homepage", "Homepage", "tag_line")
	description = frappe.db.get_value("Homepage", "Homepage", "description")

	frappe.reload_doc('maia_website', 'doctype', 'default_template')
	default_template = frappe.get_doc('Default Template', 'Default Template')
	default_template.website_title = tag_line
	default_template.title = tag_line
	default_template.subtitle = description
	default_template.button_label = _("Make an appointment")
	default_template.button_link = "/login"
	default_template.save()

	remove_app("erpnext", False, True)

	# Change portal settings default role
	portal = frappe.get_doc("Portal Settings", "Portal Settings")
	portal.default_role = "Patient"
	portal.menu = []
	portal.save()

	# Cleanup roles
	existing_roles = frappe.get_all("Has Role", fields=["name", "parent", "parenttype"])

	for r in existing_roles:
		if not frappe.db.exists(r.parenttype, r.parent):
			frappe.db.sql("""DELETE FROM `tabHas Role` WHERE name=%s""", r.name)

	# Remove old roles
	users = frappe.get_all("User")
	roles = frappe.db.sql_list("""select name from `tabRole` where name not in ("Midwife", "System Manager", "Midwife Substitute", "Patient", "Appointment User", "Administrator", "Guest", "All")""")

	for user in users:
		user_roles = frappe.get_roles(user.name)
		user = frappe.get_doc("User", user.name)

		if "Customer" in user_roles:
			user.add_roles("Patient")

		user.remove_roles(*roles)

	for role in roles:
		try:
			frappe.delete_doc("Role", role)
		except Exception as e:
			print("Role: " + role)
			print(e)