# -*- coding: utf-8 -*-
# Copyright (c) 2015, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import dateparser
from frappe.utils import nowdate


class Gynecology(Document):
	pass

@frappe.whitelist()
def get_last_cervical_smears(patient_record):
	doc = frappe.get_doc("Patient Record", patient_record)

	cervical_smears = doc.cervical_smear_table

	for cervical_smear in cervical_smears:
		cervical_smear.update({'date_time': dateparser.parse((cervical_smear.date.strip()) if (cervical_smear.date is not None) else nowdate())}, settings={'TIMEZONE': 'Europe/Paris'})

	sortedsmears = sorted(cervical_smears, key=lambda x: x.date_time, reverse=True)
	return sortedsmears[:5]


@frappe.whitelist()
def add_cervical_smear(patient_record, date, result):
	doc = frappe.get_doc("Patient Record", patient_record)

	doc.append('cervical_smear_table', {
		'date': date,
		'result': result
	})
	try:
		doc.save(ignore_permissions=True)
		return 'Success'
	except:
		raise
