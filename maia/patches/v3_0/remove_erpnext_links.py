# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
from frappe.installer import remove_app
from frappe import _
from frappe.utils import update_progress_bar
from frappe.cache_manager import clear_user_cache

def execute():
	l = 12
	frappe.delete_doc("Dashboard Chart Source", "Account Balance Timeline")

	erpnext_modules = ["Selling", "Accounts", "Assets", "Buying", \
		"HR", "Maintenance", "Manufacturing", "Quality Management", "Regional", "Stock", "Support"]

	notifications = frappe.get_all("Notification")
	for notification in notifications:
		frappe.delete_doc("Notification", notification.name)
	update_progress_bar("Cleaning up ERPNext", 1, l)

	print_formats = frappe.get_all("Print Format", filters={"module": ["in", erpnext_modules]})

	for print_format in print_formats:
		frappe.delete_doc("Print Format", print_format.name)
	update_progress_bar("Cleaning up ERPNext", 2, l)

	data_migration_plans = frappe.get_all("Data Migration Plan")

	for data_migration_plan in data_migration_plans:
		frappe.delete_doc("Data Migration Plan", data_migration_plan.name)
	update_progress_bar("Cleaning up ERPNext", 3, l)

	erpnext_doctypes = [x["name"] for x in frappe.get_all("DocType", filters={"module": ["in", erpnext_modules]})]

	custom_fields = frappe.get_all("Custom Field", filters={"options": ["in", erpnext_doctypes], "fieldtype": "Link"})
	for custom_field in custom_fields:
		frappe.delete_doc("Custom Field", custom_field.name)
	update_progress_bar("Cleaning up ERPNext", 4, l)

	property_setters = frappe.get_all("Property Setter", filters={"doc_type": ["in", erpnext_doctypes]})
	for property_setter in property_setters:
		frappe.delete_doc("Property Setter", property_setter.name)
	update_progress_bar("Cleaning up ERPNext", 5, l)
	
	print_formats = frappe.get_all("Print Format", filters={"doc_type": ["in", erpnext_doctypes]})
	for print_format in print_formats:
		frappe.delete_doc("Print Format", print_format.name)
	update_progress_bar("Cleaning up ERPNext", 6, l)

	# Add Facture Maia
	frappe.reload_doctype('Print Format')
	frappe.make_property_setter({
		'doctype_or_field': "DocType",
		'doctype': "Print Format",
		'property': "default_print_format",
		'value': "Facture Maia",
	})
	update_progress_bar("Cleaning up ERPNext", 7, l)

	# Move home page to new web page
	tag_line = frappe.db.get_value("Homepage", "Homepage", "tag_line")
	description = frappe.db.get_value("Homepage", "Homepage", "description")

	frappe.reload_doc('website', 'doctype', 'web_page')
	frappe.reload_doc('website', 'doctype', 'website_theme')
	frappe.reload_doc('maia_website', 'doctype', 'default_template')
	frappe.reload_doc('maia_website', 'doctype', 'default_template_body')
	default_template = frappe.get_doc('Default Template', 'Default Template')
	default_template.website_title = tag_line
	default_template.title = tag_line
	default_template.subtitle = description
	default_template.button_label = _("Make an appointment")
	default_template.button_link = "/login"
	default_template.save()
	update_progress_bar("Cleaning up ERPNext", 8, l)

	# Change portal settings default role
	portal = frappe.get_doc("Portal Settings", "Portal Settings")
	portal.default_role = "Patient"
	portal.menu = []
	portal.save()
	update_progress_bar("Cleaning up ERPNext", 9, l)

	# Remove ERPNext
	remove_app("erpnext", False, True)
	frappe.clear_cache()

	if "france_reports" in frappe.get_installed_apps():
		remove_app("france_reports", False, True)
		frappe.clear_cache()

	if hasattr(frappe.local, 'doc_events_hooks'):
		frappe.local.doc_events_hooks = {}

	# Cleanup roles
	existing_roles = frappe.get_all("Has Role", fields=["name", "parent", "parenttype"])

	for r in existing_roles:
		if not frappe.db.exists(r.parenttype, r.parent):
			frappe.db.sql("""DELETE FROM `tabHas Role` WHERE name=%s""", r.name)
	
	frappe.db.commit()
	update_progress_bar("Cleaning up ERPNext", 10, l)

	values = ["company", "stock_uom", "buying_price_list", "set_qty_in_transactions_based_on_serial_no_input", \
		"auto_accounting_for_stock", "maintain_same_rate", "cust_master_name", "allow_negative_stock", "item_naming_by", "maintain_same_sales_rate", \
		"supp_master_name", "territory", "customer_group"]
	for value in values:
		frappe.defaults.clear_default(value)

	clear_user_cache()
	update_progress_bar("Cleaning up ERPNext", 11, l)

	cleanup_dynamic_links()
	update_progress_bar("Cleaning up ERPNext", 12, l)

def cleanup_dynamic_links():
	# Contacts
	contacts = frappe.get_all("Dynamic Link", filters={"parenttype": "Contact", "link_doctype": "Customer"}, fields=["name", "link_name"])

	for contact in contacts:
		contact_links = frappe.get_all("Dynamic Link", filters={"parenttype": "Contact", "link_name": contact.link_name})

		if len(contact_links) > 1:
			frappe.delete_doc("Dynamic Link", contact.name, force=True)
		else:
			frappe.db.set_value("Dynamic Link", contact.name, "link_doctype", "Patient Record")

	# Addresses
	addresses = frappe.get_all("Dynamic Link", filters={"parenttype": "Address", "link_doctype": "Customer"}, fields=["name", "link_name"])

	for address in addresses:
		address_links = frappe.get_all("Dynamic Link", filters={"parenttype": "Address", "link_name": address.link_name})

		if len(address_links) > 1:
			frappe.delete_doc("Dynamic Link", address.name, force=True)
		else:
			frappe.db.set_value("Dynamic Link", address.name, "link_doctype", "Patient Record")
