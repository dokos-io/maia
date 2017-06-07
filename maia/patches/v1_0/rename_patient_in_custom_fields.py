from __future__ import unicode_literals
import frappe

from frappe.model.utils.rename_field import rename_field
from frappe.utils.fixtures import sync_fixtures

def execute():
    """ 
    Rename patient field in Sales Invoice, Customer and Contact to patient_record
    """
    if "patient_record" in frappe.db.get_table_columns("Sales Invoice"):
        pass
    else:
        frappe.db.sql("""ALTER TABLE `tabSales Invoice` CHANGE COLUMN `patient` `patient_record` VARCHAR(255) """)

    if "patient_record" in frappe.db.get_table_columns("Customer"):
        pass
    else:
        frappe.db.sql("""ALTER TABLE `tabCustomer` CHANGE COLUMN `patient` `patient_record` VARCHAR(255) """)

    if "patient_record" in frappe.db.get_table_columns("Contact"):
        pass
    else:
        frappe.db.sql("""ALTER TABLE `tabContact` CHANGE COLUMN `patient` `patient_record` VARCHAR(255) """)
