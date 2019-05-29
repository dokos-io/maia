# coding=utf-8
# Copyright (c) 2018, DOKOS and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import os
from frappe.printing.doctype.print_format.print_format import make_default

def install_chart_of_accounts():
	path = os.path.join(frappe.get_module_path('maia_accounting'), "doctype", "accounting_item", "plan_comptable.json")
	pc = frappe.get_file_json(path) 
	for p in pc: 
		try: 
			doc = frappe.new_doc("Accounting Item") 
			doc.accounting_item = p 
			doc.update(pc[p]) 
			doc.insert(ignore_permissions=True) 
		except Exception as e: 
			print(e)

	frappe.db.commit()

def create_professional_contact_card():
	users = frappe.db.get_all("User", fields=["name", "full_name"])
	if users:
		user = users[0]["name"]
		full_name = users[0]["full_name"]

		prof_card = frappe.get_doc({
			"doctype": "Professional Information Card",
			"user": user,
			"full_name": full_name
		})
		prof_card.insert(ignore_permissions=True)

def set_default_print_formats():
	names = ["Patient Folder", "Prenatal Interview Folder", "Perineum Rehabilitation Folder", "Gynecology Folder", \
		"Pregnancy Folder", "Postnatal Consultation", "Birth Preparation Consultation", "Perineum Rehabilitation Consultation", \
		"Free Consultation", "Early Postnatal Consultation", "Gynecological Consultation", "Pregnancy Consultation", "Drug Prescription",
		"Quittance Maia"]

	for name in names:
		print_format = frappe.get_doc("Print Format", name)
		frappe.make_property_setter({
			'doctype_or_field': "DocType",
			'doctype': print_format.doc_type,
			'property': "default_print_format",
			'value': name,
		})

def make_web_page():
	users = frappe.db.get_all("User", fields=["full_name"])
	if users:
		full_name = users[0]["full_name"]

	default_template = frappe.get_doc('Default Template', None)
	default_template.website_title = full_name
	default_template.title = full_name
	default_template.subtitle = _("Please login to make an appointment")
	default_template.button_label = _("Make an appointment")
	default_template.button_link = "/login"
	default_template.save()

def web_portal_settings():
	frappe.reload_doctype("Portal Settings")
	items = frappe.get_all("Portal Menu Item", fields=['name', 'title', 'route', 'enabled'])

	for item in items:
		if not (item.route == "/appointment" or item.route == "/my-appointments"):
			frappe.db.set_value("Portal Menu Item", item.name, "enabled", 0)

	frappe.db.commit()

def disable_signup():
	frappe.db.set_value("Website Settings", "Website Settings", "disable_signup", 1)
	frappe.db.commit()

def disable_guest_access():
	frappe.db.set_value("Role", "Guest", "desk_access", 0)
	frappe.db.commit()

def send_welcome_email():
	users = frappe.get_all("User", filters={"name": ["not in", ["Guest", "Administrator"]]})

	if users:
		user = frappe.get_doc("User", users[0]["name"])
		user.send_welcome_mail_to_user()