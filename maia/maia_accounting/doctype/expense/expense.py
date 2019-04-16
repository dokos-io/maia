# -*- coding: utf-8 -*-
# Copyright (c) 2019, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from maia.maia_accounting.controllers.accounting_controller import AccountingController

class Expense(AccountingController):
	def validate(self):
		self.set_status()

	def before_submit(self):
		self.set_outstanding_amount()