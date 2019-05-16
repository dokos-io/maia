# Copyright (c) 2018, DOKOS and Contributors

import frappe

def check_default_web_role(doc, method):
	if doc.disable_signup == 0:
		portal_settings = frappe.get_doc('Portal Settings', None)
		portal_settings.default_role = "Patient"
		portal_settings.save(ignore_permissions=True)
