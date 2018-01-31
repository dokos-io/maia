# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from maia.maia.invoicing import create_and_submit_invoice, get_customer_name, cancel_consultation_and_invoice, remove_cancelled_invoice
from frappe.utils import get_datetime

class PregnancyConsultation(Document):
		def before_insert(self):
			remove_cancelled_invoice(self)

		def validate(self):
			remove_cancelled_invoice(self)

		def on_submit(self):
			get_customer_name(self)
			create_and_submit_invoice(self)

		def on_cancel(self):
			cancel_consultation_and_invoice(self)

@frappe.whitelist()
def get_base_weight(patient_record):
	patient = frappe.get_doc("Patient Record", patient_record)

	return patient.weight


def nearest(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))
