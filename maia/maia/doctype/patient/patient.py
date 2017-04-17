# -*- coding: utf-8 -*-
# Copyright (c) 2017, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.naming import make_autoname
from frappe import _, msgprint, throw
from frappe.utils import cstr, has_gravatar
import frappe.defaults
from frappe.model.document import Document
from frappe.geo.address_and_contact import load_address_and_contact
from erpnext.utilities.transaction_base import TransactionBase


class Patient(Document):
        def get_feed(self):
                return self.name
                         
        def onload(self):
                """Load address in `__onload`"""
                load_address_and_contact(self, "patient")
                self.load_dashboard_info()

        def load_dashboard_info(self):
                billing_this_year = frappe.db.sql("""select sum(debit_in_account_currency) - sum(credit_in_account_currency), account_currency
                from `tabGL Entry` where voucher_type='Sales Invoice' and party_type='Customer' and party=%s and fiscal_year = %s""", (self.customer, frappe.db.get_default("fiscal_year")))

                total_unpaid = frappe.db.sql("""select sum(outstanding_amount) from `tabSales Invoice` where customer=%s and docstatus = 1""", self.customer)

                info = {}
                info["billing_this_year"] = billing_this_year[0][0] if billing_this_year else 0
                info["currency"] = billing_this_year[0][1] if billing_this_year else get_default_currency()
                info["total_unpaid"] = total_unpaid[0][0] if total_unpaid else 0

                self.set_onload('dashboard_info', info)

        def autoname(self):
                # concat first and last name
                self.patient_name = " ".join(filter(None,
                        [cstr(self.get(f)).strip() for f in ["patient_first_name", "patient_last_name"]]))
                                                

        def update_address_links(self):
              addresses = frappe.db.sql("""select parent from `tabDynamic Link` where parenttype = 'Address' and link_doctype = 'Patient' and link_name = %s""", (self.name))

              #check if customer is linked to each parent
              for address in addresses:
                      try:
                              customer_link = frappe.db.sql("""select * from `tabDynamic Link` where parent = %s and parenttype = 'Address' and link_doctype = 'Customer' and link_name = %s """, (address, self.customer))
                              pass
                              
                      except:
                              address_to_update = frappe.get_doc({"doctype":"Address", "name":address})
                              address_to_update.append('links', { "link_doctype": "Customer", "link_name": self.customer }).insert(ignore_permissions=True)
                      

        def on_update(self):
                self.autoname()
                self.update_address_links()

                updating_customer(self)
                frappe.db.set_value(self.doctype,self.name,"change_in_patient",0)
                self.reload()


        def after_insert(self):
                create_customer_from_patient(self)

        def validate(self):
                self.autoname()

                updating_customer(self)
        
        def on_trash(self):
                self.delete_patient_address()

        def after_rename(self, olddn, newdn, merge=False):
                frappe.db.set(self, 'patient_name', newdn)
                set_field = ", name=%(newdn)s"                                                                                                                                                                                
def create_customer_from_patient(doc):
                
                customer =  frappe.get_doc({
                        "doctype": "Customer",
                        "customer_name": doc.patient_name,
                        "patient": doc.name,
                        "customer_type": 'Individual',
                        "customer_group": _('Individual'),
                        "territory": _('All Territories')
                        }).insert(ignore_permissions=True)

                frappe.db.set_value("Patient", doc.name, "Customer", customer.name)

                doc.reload()

def updating_customer(self):
        frappe.db.sql("""update `tabCustomer` set customer_name=%s, modified=NOW() where patient=%s""",(self.patient_name, self.name))