# -*- coding: utf-8 -*-
# Copyright (c) 2020, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

keydict = {
	'currency': 'currency'
}

class MaiaSettings(Document):
	def on_update(self):
		for key in keydict:
			frappe.db.set_default(key, self.get(keydict[key], ''))

		if self.currency:
			frappe.db.set_value("Currency", self.currency, "enabled", 1)
