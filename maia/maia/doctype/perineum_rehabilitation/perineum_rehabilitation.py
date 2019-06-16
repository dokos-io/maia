# -*- coding: utf-8 -*-
# Copyright (c) 2017, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class PerineumRehabilitation(Document):
	pass

@frappe.whitelist()
def get_patient_sports(patient):
	doc = frappe.get_doc("Patient Record", patient)

	result = []
	for sport in doc.patient_sports:
		result.append({"sport": sport.sport, "note": sport.note})

	return result