from __future__ import unicode_literals
import frappe

def execute():
    frappe.db.set_value("Website Settings", "Website Settings", "disable_signup", 1)
    frappe.db.commit()
