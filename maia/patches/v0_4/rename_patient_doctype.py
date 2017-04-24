import frappe

def execute():
    if frappe.db.table_exists("Patient") and not frappe.db.table_exists("Patient Record"):
        frappe.rename_doc("DocType", "Patient", "Patient Record")

        frappe.delete_doc('DocType', 'Patient')
