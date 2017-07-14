# -*- coding: utf-8 -*-
# Copyright (c) 2017, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import _
from erpnext.accounts.utils import get_account_currency
from erpnext.controllers.accounts_controller import AccountsController

class PersonalDebit(AccountsController):
	def validate(self):
                self.validate_bank_account()

        def on_submit(self):
                self.make_journal_entry()

        def on_cancel(self):
                jv = frappe.get_doc("Journal Entry", self.journal_entry)
                jv.cancel()

        def on_trash(self):
                jv = frappe.get_doc("Journal Entry", self.journal_entry)
                jv.delete()

        def validate_bank_account(self):
                bank_account_type = frappe.db.get_value("Account", self.bank_account, "account_type")

                if bank_account_type not in ["Bank"]:
                        frappe.throw(_("Bank Account {0} must be a Bank Account")
                                     .format(self.bank_account))

                account_currency = get_account_currency(self.bank_account)
                company_currency = frappe.db.get_value("Company", self.company, "default_currency")
                if account_currency != company_currency:
                        frappe.throw(_("Currency of the Bank Account must be {0}").format(company_currency))

        def make_journal_entry(self):
                jv = frappe.new_doc("Journal Entry")
                jv.posting_date = self.posting_date
                jv.company = self.company
                jv.user_remark = self.remarks
                jv.set("accounts", [
                        {
                                "account": self.personal_debit_account,
                                "debit_in_account_currency": abs(flt(self.debit_amount)),
                                "credit_in_account_currency": 0,
                        }, {
                                "account": self.bank_account,
                                "credit_in_account_currency": abs(flt(self.debit_amount)),
                                "debit_in_account_currency": 0,
                        }
                ])
                jv.insert()
                jv.submit()

                frappe.db.set_value(self.doctype, self.name, "journal_entry", jv.name)
