# -*- coding: utf-8 -*-
# Copyright (c) 2017, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.naming import make_autoname
from frappe import _
from frappe.utils import cstr, cint, has_gravatar, add_years, get_timestamp
import frappe.defaults
from frappe.model.document import Document
from frappe.contacts.address_and_contact import load_address_and_contact
from erpnext.utilities.transaction_base import TransactionBase
from erpnext.accounts.party import validate_party_accounts
from erpnext.controllers.queries import get_filters_cond
from frappe.desk.reportview import get_match_cond


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

        total_unpaid = frappe.db.sql(
            """select sum(outstanding_amount) from `tabSales Invoice` where customer=%s and docstatus = 1""", self.customer)

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
            count = frappe.db.sql("""select ifnull(MAX(CAST(SUBSTRING_INDEX(name, ' ', -1) AS UNSIGNED)), 0) from `tabPatient Record` where name like %s""",
                                  "%{0} - %".format(self.patient_name), as_list=1)[0][0]
            count = cint(count) + 1

            return "{0} - {1}".format(self.patient_name, cstr(count))

        return self.patient_name

    def update_address_links(self):
        address_names = frappe.get_all('Dynamic Link', filters={
            "parenttype": "Address",
            "link_doctype": "Patient Record",
            "link_name": self.name
        }, fields=["parent as name"])

        # check if customer is linked to each parent
        for address_name in address_names:
            address = frappe.get_doc('Address', address_name.get('name'))
            if not address.has_link('Customer', self.customer):
                address.append('links', dict(
                    link_doctype='Customer', link_name=self.customer))
                address.save()

    def validate(self):
        self.patient_name = " ".join(filter(None,
                                            [cstr(self.get(f)).strip() for f in ["patient_first_name", "patient_last_name"]]))

        self.update_address_links()

        updating_customer(self)

    def on_update(self):
        self.update_address_links()

        updating_customer(self)
        frappe.db.set_value(self.doctype, self.name, "change_in_patient", 0)
        self.reload()

    def after_insert(self):
        create_customer_from_patient(self)

    def on_trash(self):
        if frappe.db.exists("Customer", self.customer):
            doc = frappe.get_doc('Customer', self.customer)
            doc.delete()

    def after_rename(self, olddn, newdn, merge=False):
        frappe.rename_doc('Customer', self.customer, newdn, force=True,
                          merge=True if frappe.db.exists('Customer', newdn) else False)


def create_customer_from_patient(doc):

    customer = frappe.get_doc({
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
    frappe.db.sql("""update `tabCustomer` set customer_name=%s, modified=NOW() where patient_record=%s""",
                  (self.patient_name, self.name))


def get_timeline_data(doctype, name):
    '''returns timeline data for the past one year'''
    from frappe.desk.form.load import get_communication_data
    patient_record = frappe.get_doc(doctype, name)

    out = {}

    conditions = ' and creation > {0}'.format(add_years(None, -1).strftime('%Y-%m-%d'))
    data = frappe.db.sql("""
        SELECT
            count(name), date(posting_date)
        FROM
            `tabSales Invoice`
        WHERE
            patient_record = %(pat_rec)s
            and status!="Cancelled" {conditions}
        GROUP BY
            posting_date""".format(conditions=conditions),{"pat_rec": patient_record.name}, as_dict=0)

    timeline_items = dict(data)

    for count, date in timeline_items.iteritems():
        timestamp = get_timestamp(date)
        out.update({timestamp: count})

    return out


@frappe.whitelist()
def invite_user(patient):
    patient_record = frappe.get_doc("Patient Record", patient)

    if not patient_record.email_id:
        frappe.throw(_("Please set Email Address"))

    try:
        user = frappe.get_doc({
            "doctype": "User",
            "first_name": patient_record.patient_first_name,
            "last_name": patient_record.patient_last_name,
            "email": patient_record.email_id,
            "user_type": "Website User",
            "send_welcome_email": 1
        }).insert(ignore_permissions=True)

        user.append("roles", {
            "doctype": "Has Role",
            "role": "Customer"
        })

        user.save()

    except:
        user = frappe.get_doc("User", patient_record.email_id)
        if user:
            try:
                frappe.delete_doc("User", user.name)
            except:
                return
        return

    try:
        contact = frappe.get_doc({
            "doctype": "Contact",
            "first_name": patient_record.patient_first_name,
            "last_name": patient_record.patient_last_name,
            "email_id": patient_record.email_id,
            "user": user.name
        }).insert(ignore_permissions=True)
        contact.save()

        contact.append('links', dict(link_doctype='Customer',
                                     link_name=patient_record.customer))
        contact.append('links', dict(link_doctype='Patient Record',
                                     link_name=patient_record.name))
        contact.save()

    except:
        pass

    return user.name


def get_users_for_website(doctype, txt, searchfield, start, page_len, filters):
    conditions = []
    return frappe.db.sql("""select name, concat_ws(' ', first_name, middle_name, last_name)
        from `tabUser`
        where enabled=1
            and name not in ("Guest", "Administrator")
            and ({key} like %(txt)s
                or full_name like %(txt)s)
            {fcond} {mcond}
        order by
            if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
            if(locate(%(_txt)s, full_name), locate(%(_txt)s, full_name), 99999),
            idx desc,
            name, full_name
        limit %(start)s, %(page_len)s""".format(**{
        'key': searchfield,
        'fcond': get_filters_cond(doctype, filters, conditions),
        'mcond': get_match_cond(doctype)
    }), {
        'txt': "%%%s%%" % txt,
        '_txt': txt.replace("%", ""),
        'start': start,
        'page_len': page_len
    })
