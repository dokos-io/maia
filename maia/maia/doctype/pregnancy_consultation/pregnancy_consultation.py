# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from maia.maia.invoicing import create_and_submit_invoice, get_customer_name, cancel_consultation_and_invoice, remove_cancelled_invoice
from frappe.utils import get_datetime
from maia.maia.utils import check_folder_and_record

class PregnancyConsultation(Document):
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

@frappe.whitelist()
def get_comparison_weight(patient_record):
	weights = {}
	patient = frappe.get_doc("Patient Record", patient_record)

	weights.update({'base_weight': patient.weight})

	last_weight = _get_last_pregnancy_consultation_weight(patient_record)
	if last_weight:
		weights.update({'last_weight': last_weight[0].weight})
	else:
		weights.update({'last_weight': patient.weight})

	return weights


def _get_last_pregnancy_consultation_weight(patient_record):
	dates = frappe.get_all("Pregnancy Consultation", filters={"patient_record": patient_record, "docstatus": 1}, fields=["name", "consultation_date"])

	if all(date.consultation_date is None for date in dates) == False:
		last_consultation_date = max(date.consultation_date for date in dates if date.consultation_date is not None)
	else:
		last_consultation_date = "1900-01-01"

	last_pregnancy_consultation = frappe.get_all("Pregnancy Consultation", filters={"patient_record": patient_record, "docstatus": 1, "consultation_date": last_consultation_date}, fields=['name', 'weight'])

	return last_pregnancy_consultation

def nearest(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))
