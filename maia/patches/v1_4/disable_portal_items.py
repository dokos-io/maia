from __future__ import unicode_literals
import frappe

def execute():
    frappe.reload_doctype("Portal Settings")

    items = frappe.get_all("Portal Menu Item",fields=['name', 'title', 'route', 'enabled'])

    for item in items:
        if item.route == "/appointment":
            pass
        else:
            frappe.db.set_value("Portal Menu Item", item.name, "enabled", 0)
