from __future__ import unicode_literals
import frappe

def execute():
    companies =  frappe.get_all("Company")
    practitioners = frappe.get_all("Professional Information Card")

    for practitioner in practitioners:
        frappe.set_value("Professional Information Card", practitioner.name, "company", companies[0].name)
        frappe.db.commit()
