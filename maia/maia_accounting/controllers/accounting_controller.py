# Copyright (c) 2019, Dokos and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from maia.maia_accounting.controllers.status_updater import StatusUpdater

class AccountingController(StatusUpdater):
	def set_outstanding_amount(self):
		self.outstanding_amount = self.amount