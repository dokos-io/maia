# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.desk.doctype.desktop_icon.desktop_icon import set_hidden_list


def execute():
	frappe.reload_doctype("Portal Settings")

	items = frappe.get_all("Portal Menu Item", fields=[
						   'name', 'title', 'route', 'enabled'])

	for item in items:
		if item.route == "/appointment" or item.route == "/my-appointments":
			pass
		else:
			frappe.db.set_value("Portal Menu Item", item.name, "enabled", 0)

	frappe.db.commit()
