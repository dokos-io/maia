# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_years, get_timestamp, getdate, cint
import math
import pandas as pd
import numpy as np

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

		counted_in_parity = cint(frappe.db.get_value("Delivery Way", pregnancy.delivery_way, "used_in_parity"))
		if counted_in_parity:
			if not cint(pregnancy.multiple_pregnancy):
				parity += 1
			else:
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

		counted_in_parity = cint(frappe.db.get_value("Delivery Way", pregnancy.delivery_way, "used_in_parity"))
		if counted_in_parity:
			children = 0
			if pregnancy.date_time is not None:
				children += 1
			if cint(pregnancy.twins):
				if pregnancy.birth_datetime_2 is not None:
					children += 1
			if cint(pregnancy.triplets):
				if pregnancy.birth_datetime_3 is not None:
					children += 1

			parity += children

	return gravidity, parity

def get_timeline_data(doctype, name):
	'''returns timeline data for the past one year'''
	from frappe.desk.form.load import get_communication_data
	patient_record = frappe.get_doc(doctype, name)

	return {}
	#TODO: Rewrite method
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

def get_gestational_age(pregnancy, date):
	if pregnancy.beginning_of_pregnancy:
		weeks = get_gestational_weeks(pregnancy.beginning_of_pregnancy, date) + 2
		days = get_gestational_days(pregnancy.beginning_of_pregnancy, date)
	elif pregnancy.expected_term:
		weeks = math.floor((287 - days_diff(getdate(date), getdate(pregnancy.expected_term))) / 7)
		days = math.floor(((287 - days_diff(getdate(date), getdate(pregnancy.expected_term))) / 7 - weeks) * 7)
	elif pregnancy.last_menstrual_period:
		weeks = get_gestational_weeks(pregnancy.last_menstrual_period, date)
		days = get_gestational_days(pregnancy.last_menstrual_period, date)
	else:
		weeks = 0
		days = 0

	return weeks, days

def get_gestational_weeks(start_date, end_date):
	return math.floor(weeks_diff(getdate(start_date), getdate(end_date)))

def get_gestational_days(start_date, end_date):
	return days_diff(getdate(start_date), getdate(end_date)) - math.floor(weeks_diff(getdate(start_date), getdate(end_date)) * 7)

def weeks_diff(start, end):
	x = pd.to_datetime(end) - pd.to_datetime(start)
	return int(x / np.timedelta64(1, 'W'))

def days_diff(start, end):
	x = pd.to_datetime(end) - pd.to_datetime(start)
	return int(x / np.timedelta64(1, 'D'))