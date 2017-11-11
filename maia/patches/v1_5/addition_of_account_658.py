from __future__ import unicode_literals
import frappe


def execute():
    companies = frappe.get_all("Company")

    for company in companies:
        abbr = frappe.get_value("Company", company.name, "abbr")
        try:
            existing_account = frappe.get_doc(
                "Account", "65 - Autres Charges de Gestion Courante - " + abbr)

        except:
            parent_account = frappe.get_doc({
                "doctype": "Account",
                "root_type": "Expense",
                "company": company.name,
                "parent_account": "Charges - " + abbr,
                "account_name": "65 - Autres Charges de Gestion Courante",
                "is_group": 1})

            parent_account.insert(ignore_permissions=True)

            child_account = frappe.get_doc({
                "doctype": "Account",
                "root_type": "Expense",
                "company": company.name,
                "parent_account": "65 - Autres Charges de Gestion Courante - " + abbr,
                "account_name": "658 - Charges Diverses de Gestion Courante",
                "account_type": "Expense Account",
                "is_group": 0})

            child_account.insert(ignore_permissions=True)

    frappe.db.commit()
