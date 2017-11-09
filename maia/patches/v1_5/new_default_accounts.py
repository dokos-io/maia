from __future__ import unicode_literals
import frappe


def execute():
    companies = frappe.get_all("Company")

    for company in companies:
        abbr = frappe.get_value("Company", company.name, "abbr")
        fee_account = "709-Honoraires rétrocédés - " + abbr
        personal_debit_account = "108900-Compte de l'exploitant - " + abbr

        if frappe.db.exists('Account', fee_account):
            frappe.db.set_value('Company', company.name,
                                'fee_account', fee_account)

        if frappe.db.exists('Account', personal_debit_account):

    frappe.db.commit()
