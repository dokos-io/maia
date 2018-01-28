# -*- coding: utf-8 -*-
# Copyright (c) 2015, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from maia.maia.utils import parity_gravidity_calculation

class Pregnancy(Document):
	def onload(self):
		self.set_gravidity_and_parity()

	def on_update(self):
		self.set_gravidity_and_parity()

	def set_gravidity_and_parity(self):
		gravidity, parity = parity_gravidity_calculation(self.patient_record)

		self.gravidity = gravidity
		self.parity = parity
