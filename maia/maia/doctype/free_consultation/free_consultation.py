# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from maia.maia.invoicing import create_and_submit_invoice, get_customer_name, cancel_consultation_and_invoice, remove_cancelled_invoice
from maia.maia.utils import check_folder_and_record

class FreeConsultation(Document):
	def before_insert(self):
		remove_cancelled_invoice(self)
		check_folder_and_record(self)

	def validate(self):
		remove_cancelled_invoice(self)

	def on_submit(self):
		get_customer_name(self)
		create_and_submit_invoice(self)

	def on_cancel(self):
		cancel_consultation_and_invoice(self)
