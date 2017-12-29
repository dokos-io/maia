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

class CashDeposit(AccountsController):
    def validate(self):
        self.validate_cash_deposit_account()

    def on_submit(self):
        self.make_journal_entry()

    def on_cancel(self):
        jv = frappe.get_doc("Journal Entry", self.journal_entry)
        jv.cancel()

    def on_trash(self):
        jv = frappe.get_doc("Journal Entry", self.journal_entry)
        jv.delete()

    def validate_cash_deposit_account(self):
        cash_account_type = frappe.db.get_value(
            "Account", self.cash_deposit_account, "account_type")

        if cash_account_type not in ["Bank"]:
            frappe.throw(_("Cash Deposit Account {0} must be a Bank Account")
                         .format(self.cash_deposit_account))

        account_currency = get_account_currency(self.cash_deposit_account)
        company_currency = frappe.db.get_value(
            "Company", self.company, "default_currency")
        if account_currency != company_currency:
            frappe.throw(
                _("Currency of the Cash Deposit Account must be {0}").format(company_currency))

    def make_journal_entry(self):
        jv = frappe.new_doc("Journal Entry")
        jv.posting_date = self.posting_date
        jv.company = self.company
        jv.user_remark = self.remarks
        jv.set("accounts", [
            {
                "account": self.cash_deposit_account,
                "debit_in_account_currency": abs(flt(self.deposit_amount)),
                "credit_in_account_currency": 0,

            }, {
                "account": self.cash_account,
                "credit_in_account_currency": abs(flt(self.deposit_amount)),
                "debit_in_account_currency": 0,

            },  {
                "account": self.internal_transfer_account,
                "credit_in_account_currency": 0,
                "debit_in_account_currency": abs(flt(self.deposit_amount)),

            }, {
                "account": self.internal_transfer_account,
                "credit_in_account_currency": abs(flt(self.deposit_amount)),
                "debit_in_account_currency": 0,

            }
        ])
        jv.insert()
        jv.submit()

        frappe.db.set_value(self.doctype, self.name, "journal_entry", jv.name)
