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
                self.make_gl_entries()

        def on_cancel(self):
                frappe.db.sql("""delete from `tabGL Entry` where voucher_type = 'Cash Deposit' and voucher_no=%s""", self.name)


        def validate_cash_deposit_account(self):
                cash_account_type = frappe.db.get_value("Account", self.cash_deposit_account, "account_type")

                if cash_account_type not in ["Bank"]:
                        frappe.throw(_("Cash Deposit Account {0} must be a Bank Account")
                                     .format(self.cash_deposit_account))

                account_currency = get_account_currency(self.cash_deposit_account)
                company_currency = frappe.db.get_value("Company", self.company, "default_currency")
                if account_currency != company_currency:
                        frappe.throw(_("Currency of the Cash Deposit Account must be {0}").format(company_currency))


        def make_gl_entries(self):
                gl_entries = []
                net_pl_balance = 0
                gl_accounts = [self.cash_deposit_account, self.cash_account, self.internal_transfer_account]

                frappe.logger().debug(self)
                for account in gl_accounts:
                        acc = frappe.get_doc("Account", account)
                        gl_entries.append(self.get_gl_dict({
                                "account": acc.name,
                                "account_currency": acc.account_currency,
                                "debit_in_account_currency": abs(flt(self.deposit_amount)) if account!=gl_accounts[1] else 0,
                                "debit": abs(flt(self.deposit_amount)) if account!=gl_accounts[1] else 0,
                                "credit_in_account_currency": abs(flt(self.deposit_amount)) if account!=gl_accounts[0] else 0,
                                "credit": abs(flt(self.deposit_amount)) if account!=gl_accounts[0] else 0

                        }))

                from erpnext.accounts.general_ledger import make_gl_entries
                make_gl_entries(gl_entries)
