# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# License: GNU General Public License v3. See license.txt

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


	remove_app("erpnext", False, True)
	