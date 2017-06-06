# -*- coding: utf-8 -*-
# Copyright (c) 2017, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.naming import make_autoname
from frappe import _, msgprint, throw
from frappe.utils import cstr, cint, has_gravatar
import frappe.defaults
from frappe.model.document import Document
from frappe.geo.address_and_contact import load_address_and_contact
from erpnext.utilities.transaction_base import TransactionBase
from erpnext.accounts.party import validate_party_accounts, get_timeline_data

class PatientRecord(Document):
        def get_feed(self):
                return self.patient_name
        
        def onload(self):
                """Load address in `__onload`"""
                load_address_and_contact(self, "patient_record")
                self.load_dashboard_info()

        def load_dashboard_info(self):
                billing_this_year = frappe.db.sql("""select sum(debit_in_account_currency), account_currency
                from `tabGL Entry` where voucher_type='Sales Invoice' and party_type='Customer' and party=%s and fiscal_year = %s""", (self.customer, frappe.db.get_default("fiscal_year")))

                total_unpaid = frappe.db.sql("""select sum(outstanding_amount) from `tabSales Invoice` where customer=%s and docstatus = 1""", self.customer)

                info = {}
                info["billing_this_year"] = billing_this_year[0][0] if billing_this_year else 0
                info["currency"] = billing_this_year[0][1] if billing_this_year else get_default_currency()
                info["total_unpaid"] = total_unpaid[0][0] if total_unpaid else 0

                self.set_onload('dashboard_info', info)

        def autoname(self):
                self.patient_name = " ".join(filter(None,
                        [cstr(self.get(f)).strip() for f in ["patient_first_name", "patient_last_name"]]))

                self.name = self.get_patient_name()
                

        def get_patient_name(self):
                if frappe.db.get_value("Patient Record", self.patient_name):
                        count = frappe.db.sql("""select ifnull(MAX(CAST(SUBSTRING_INDEX(name, ' ', -1) AS UNSIGNED)), 0) from `tabPatient Record` where name like %s""", "%{0} - %".format(self.patient_name), as_list=1)[0][0]
                        count = cint(count) + 1

                        return "{0} - {1}".format(self.patient_name, cstr(count))

                return self.patient_name



        def update_address_links(self):
              address_names = frappe.get_all('Dynamic Link', filters={
                      "parenttype":"Address",
                      "link_doctype":"Patient Record",
                      "link_name":self.name
              }, fields=["parent as name"])

              #check if customer is linked to each parent
              for address_name in address_names:
                      address = frappe.get_doc('Address', address_name.get('name'))
                      if not address.has_link('Customer', self.customer):
                              address.append('links', dict(link_doctype='Customer', link_name=self.customer))
                              address.save()

        def validate(self):
                self.patient_name = " ".join(filter(None,
                        [cstr(self.get(f)).strip() for f in ["patient_first_name", "patient_last_name"]]))

                self.update_address_links()

                updating_customer(self)

        def on_update(self):
                self.update_address_links()

                updating_customer(self)
                frappe.db.set_value(self.doctype,self.name,"change_in_patient",0)
                self.reload()

        def after_insert(self):
                create_customer_from_patient(self)

                
def create_customer_from_patient(doc):

                customer =  frappe.get_doc({
                        "doctype": "Customer",
                        "customer_name": doc.patient_name,
                        "patient_record": doc.name,
                        "customer_type": 'Individual',
                        "customer_group": _('Individual'),
                        "territory": _('All Territories')
                        }).insert(ignore_permissions=True)

                frappe.db.set_value("Patient Record", doc.name, "Customer", customer.name)

                doc.reload()

def updating_customer(self):
        frappe.db.sql("""update `tabCustomer` set customer_name=%s, modified=NOW() where patient_record=%s""",(self.patient_name, self.name))
