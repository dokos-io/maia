from __future__ import unicode_literals
import frappe

def execute():
    frappe.reload_doctype("Portal Settings")

    items = frappe.get_all("Portal Menu Item",fields=['name', 'title', 'route', 'enabled'])

    for item in items:
        if item.route == "/appointment" or item.route == "/my-appointments":
            pass
        else:
            frappe.db.set_value("Portal Menu Item", item.name, "enabled", 0)

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
