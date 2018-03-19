# -*- coding: utf-8 -*-
# Copyright (c) 2017, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr

class MidwifeAppointmentType(Document):
	def autoname(self):
		if self.practitioner:
			self.name = "-".join(filter(None, [cstr(self.get(f)).strip() for f in ["appointment_type", "practitioner"]]))
		else:
			self.name = self.appointment_type
