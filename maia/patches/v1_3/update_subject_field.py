from __future__ import unicode_literals
import frappe

def execute():
	try:
    		frappe.db.sql("""UPDATE `tabMidwife Appointment` SET subject = patient_name """)
	except:
		pass
