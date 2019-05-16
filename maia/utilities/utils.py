# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import now_datetime

def delete_expired_sms():
	data = frappe.get_all("SMS Reminder", fields=["name", "send_on"])

	for d in data:
		if d.send_on < now_datetime():
			frappe.delete_doc("SMS Reminder", d.name, ignore_permissions=True)

def reset_portal_doctypes():
	frappe.reload_doctype("Portal Settings")

	items = frappe.get_all("Portal Menu Item", fields=[
							'name', 'title', 'route', 'enabled'])

	for item in items:
		if item.route == "/appointment" or item.route == "/my-appointments":
			pass
		else:
			frappe.db.set_value("Portal Menu Item", item.name, "enabled", 0)

	frappe.db.commit()

def custom_template_functions(functions):
	# Midwife's name
	functions.append({
		"fieldname": None,
		"label": _("Midwife's Name"),
		"fieldtype": None,
		"parent": "Custom Functions",
		"reference": None,
		"function": "frappe.get_doc('Professional Information Card', {'user': frappe.session.user}).name"
	})

	# Midwife's signature
	functions.append({
		"fieldname": None,
		"label": _("Midwife's Signature"),
		"fieldtype": None,
		"parent": "Custom Functions",
		"reference": None,
		"function": "Signature#frappe.get_doc('Professional Information Card', {'user': frappe.session.user}).signature"
	})

	return functions


@frappe.whitelist()
def delete_draft_consultation(doctype, name):
	frappe.delete_doc(doctype, name, ignore_permissions=True, ignore_missing=False)