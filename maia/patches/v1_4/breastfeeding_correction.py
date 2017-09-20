from __future__ import unicode_literals
import frappe

def execute():
    try:
        frappe.db.sql("""UPDATE `tabObstetrical Background` SET feeding = 'Breastfeeding' WHERE feeding = 'Breast-feeding'""")
    except:
        pass
