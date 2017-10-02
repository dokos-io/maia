from __future__ import unicode_literals
import frappe

def execute():
    frappe.reload_doctype("Portal Settings")

    appointment = frappe.get_all("Portal Menu Item",filters={'route': '/my-appointments'})

    if appointment == []:
        a = frappe.get_doc({
            "doctype": "Portal Menu Item",
            "title": "Mes Rendez-Vous",
            "enabled": 1,
            "route": "/my-appointments",
            "reference_doctype": "Midwife Appointment",
            "role": "Customer",
            "parent": "Portal Settings",
            "parenttype": "Portal Settings",
            "parentfield": "menu"
            })
        a.insert()


    frappe.db.commit()
