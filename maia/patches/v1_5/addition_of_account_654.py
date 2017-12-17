# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe


def execute():
    companies = frappe.get_all("Company")

    for company in companies:
        abbr = frappe.get_value("Company", company.name, "abbr")
        try:
            existing_account = frappe.get_doc("Account", "654 - Pertes sur créances irrécouvrables - " + abbr)

        except:
            child_account = frappe.get_doc({
                "doctype": "Account",
                "root_type": "Expense",
                "company": company.name,
                "parent_account": "65 - Autres Charges de Gestion Courante - " + abbr,
                "account_name": "654 - Pertes sur créances irrécouvrables",
                "account_type": "Expense Account",
                "is_group": 0})

            child_account.insert(ignore_permissions=True)

    frappe.db.commit()
