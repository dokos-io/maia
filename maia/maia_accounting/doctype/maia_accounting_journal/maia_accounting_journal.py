# -*- coding: utf-8 -*-
# Copyright (c) 2019, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class MaiaAccountingJournal(Document):
	def validate(self):
		same_type = frappe.get_all("Maia Accounting Journal", filters={"journal_type": self.journal_type, "name": ("!=", self.name)})

		if same_type:
			frappe.throw(_("Another accouting journal exists already for this journal type"))
