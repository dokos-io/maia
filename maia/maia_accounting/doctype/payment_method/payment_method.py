# -*- coding: utf-8 -*-
# Copyright (c) 2019, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class PaymentMethod(Document):
	def validate(self):
		for f in ["default_incoming", "default_outgoing"]:
			actual_default = frappe.get_all("Payment Method", filters={f: 1, "name": ["!=", self.name]})
			if actual_default:
				if getattr(self, f) == 1:
					frappe.db.set_value("Payment Method", actual_default[0].name, f, 0)
			else:
				setattr(self, f, 1)
