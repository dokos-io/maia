# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_years, get_timestamp

from six import iteritems

@frappe.whitelist()
def get_letter_head(practitioner=None, user=None):
	if practitioner:
		letterhead = frappe.db.get_value('Professional Information Card', practitioner, "letter_head")
	else:
		letterhead = frappe.db.get_value('Professional Information Card', dict(user=user), "letter_head")

	if not letterhead:
		letterhead = frappe.db.get_value('Letter Head', {"is_default": 1}, "name")

	return letterhead

@frappe.whitelist()
def parity_gravidity_calculation(patient_record):
	patient = frappe.get_doc("Patient Record", patient_record)

	gravidity = 0
	parity = 0


	for pregnancy in patient.obstetrical_backgounds:
		gravidity += 1

		counted_in_parity = frappe.db.get_value("Delivery Way", pregnancy.delivery_way)

		if counted_in_parity is not None and pregnancy.multiple_pregnancy is None:
			parity += 1

		elif counted_in_parity is not None:
			children = 0
			if pregnancy.child_full_name or pregnancy.child_gender or pregnancy.child_weight or pregnancy.child_health_state or pregnancy.feeding:
				children += 1
			if pregnancy.child_full_name_2 or pregnancy.child_gender_2 or pregnancy.child_weight_2 or pregnancy.child_health_state_2 or pregnancy.feeding_2:
				children += 1
			if pregnancy.child_full_name_3 or pregnancy.child_gender_3 or pregnancy.child_weight_3 or pregnancy.child_health_state_3 or pregnancy.feeding_3:
				children += 1

			parity += children

	pregnancies = frappe.get_all("Pregnancy", filters={'patient_record': patient_record}, fields=['name', 'date_time', 'twins', 'triplets', 'birth_datetime_2', 'birth_datetime_3', 'delivery_way'])

	for pregnancy in pregnancies:
		gravidity += 1

		counted_in_parity = frappe.db.get_value("Delivery Way", pregnancy.delivery_way)

		children = 0
		if pregnancy.date_time is not None and counted_in_parity is not None:
			children += 1

		if pregnancy.twins is not None and counted_in_parity is not None:
			if pregnancy.birth_datetime_2 is not None:
				children += 1

		if pregnancy.triplets is not None and counted_in_parity is not None:
			if pregnancy.birth_datetime_3 is not None:
				children += 1

		parity += children

	return gravidity, parity

def get_timeline_data(doctype, name):
	'''returns timeline data for the past one year'''
	from frappe.desk.form.load import get_communication_data
	patient_record = frappe.get_doc(doctype, name)

	out = {}

	conditions = ' and creation > "{0}"'.format(add_years(None, -1).strftime('%Y-%m-%d'))
	data = frappe.db.sql("""
		SELECT
			date(posting_date), count(name)
		FROM
			`tabSales Invoice`
		WHERE
			patient_record = %(pat_rec)s
			and status in ("Submitted", "Paid", "Overdue", "Unpaid") {conditions}
		GROUP BY
			posting_date""".format(conditions=conditions),{"pat_rec": patient_record.name}, as_dict=0)

	timeline_items = dict(data)

	for date, count in iteritems(timeline_items):
		timestamp = get_timestamp(date)
		out.update({timestamp: count})

	return out

def check_folder_and_record(doc):
	frappe.log_error(doc)
	if doc.docstatus == 0:
		if doc.pregnancy_folder:
			v = frappe.db.get_value("Pregnancy", doc.pregnancy_folder, "patient_record")
			if v != doc.patient_record:
				frappe.throw(_("This pregnancy folder don't belong to this patient"))

		if doc.prenatal_interview_folder:
			v = frappe.db.get_value("Prenatal Interview", doc.prenatal_interview_folder, "patient_record")
			if v != doc.patient_record:
				frappe.throw(_("This prenatal interview folder don't belong to this patient"))

		if doc.perineum_rehabilitation_folder:
			v = frappe.db.get_value("Perineum Rehabilitation", doc.perineum_rehabilitation_folder, "patient_record")
			if v != doc.patient_record:
				frappe.throw(_("This perineum rehabilitation folder don't belong to this patient"))

		if doc.gynecological_folder:
			v = frappe.db.get_value("Gynecology", frm.doc.gynecological_folder, "patient_record")
			if v != doc.patient_record:
				frappe.throw(_("This gynecology folder don't belong to this patient"))