from __future__ import unicode_literals
import frappe

def execute():
    """ 
    Drop patient column in Contact, Customer and Sales Invoice Tables
    """

    frappe.db.sql("""ALTER TABLE `tabSales Invoice` DROP COLUMN patient""")
    frappe.db.sql("""ALTER TABLE `tabCustomer` DROP COLUMN patient""")
    frappe.db.sql("""ALTER TABLE `tabContact` DROP COLUMN patient""")
