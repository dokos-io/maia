from __future__ import unicode_literals
import frappe


def execute():
    terms = frappe.get_doc({
        "doctype": "Terms and Conditions",
        "title": "Termes et Conditions Standard",
        "terms": "Membre d'une société de gestion agréée, les règlements par chèques sont acceptés."
    })
    try:
        terms.insert(ignore_permissions=True)
    except:
        pass

    frappe.db.commit()
