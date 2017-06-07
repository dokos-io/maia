from __future__ import unicode_literals
import frappe

def execute():
    """ 
    Drop patient column in Contact, Customer and Sales Invoice Tables
    """

    if "patient" in frappe.db.get_table_columns("Sales Invoice"):
        frappe.db.sql("""ALTER TABLE `tabSales Invoice` DROP COLUMN patient""")

    if "patient" in frappe.db.get_table_columns("Customer"):
        frappe.db.sql("""ALTER TABLE `tabCustomer` DROP COLUMN patient""")

    if "patient" in frappe.db.get_table_columns("Contact"):
        frappe.db.sql("""ALTER TABLE `tabContact` DROP COLUMN patient""")
