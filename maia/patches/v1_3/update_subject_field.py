from __future__ import unicode_literals
import frappe

def execute():
    frappe.db.sql("""UPDATE `tabMidwife Appointment` SET subject = patient_name """)
