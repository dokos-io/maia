# -*- coding: utf-8 -*-
# Copyright (c) 2015, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, formatdate, add_days, date_diff
from maia.maia.utils import parity_gravidity_calculation
from frappe import _

class Pregnancy(Document):
	def onload(self):
		self.set_gravidity_and_parity()

	def on_update(self):
		self.set_gravidity_and_parity()
		if not self.maternity_leave_start_date:
			self.calculate_maternity_leave()

		if self.maternity_leave_start_date and self.maternity_leave_end_date:
			total = date_diff(self.maternity_leave_end_date, self.maternity_leave_start_date) / 7

			self.maternity_leave_total = _("{0} weeks").format(total)

	def set_gravidity_and_parity(self):
		gravidity, parity = parity_gravidity_calculation(self.patient_record)

		self.gravidity = gravidity
		self.parity = parity

	def calculate_maternity_leave(self):
		if not self.parity:
			parity = 0
		else:
			parity = self.parity

		if self.number_of_foetus and self.expected_term:
			if self.number_of_foetus == 1:
				if parity < 2:
					self.maternity_leave_start_date = add_days(self.expected_term, -42)
					self.maternity_leave_end_date = add_days(self.expected_term, 60)
				else:
					self.maternity_leave_start_date = add_days(self.expected_term, -56)
					self.maternity_leave_end_date = add_days(self.expected_term, 126)

			elif self.number_of_foetus == 2:
				self.maternity_leave_start_date = add_days(self.expected_term, -84)
				self.maternity_leave_end_date = add_days(self.expected_term, 154)

			elif self.number_of_foetus > 2:
				self.maternity_leave_start_date = add_days(self.expected_term, -168)
				self.maternity_leave_end_date = add_days(self.expected_term, 154)


@frappe.whitelist()
def get_newborn_weight_data(patient_record, pregnancy, child):

	pregnancy_folder = frappe.get_doc("Pregnancy", pregnancy)

	if child == "firstchild":
		weight_field = "weight_of_the_day"
		birth_weight = pregnancy_folder.birth_weight
		release_weight = pregnancy_folder.release_weight
		birth_date = pregnancy_folder.date_time
		release_date = pregnancy_folder.release_date
		gender = pregnancy_folder.gender

	elif child == "secondchild":
		weight_field = "weight_of_the_day_2"
		birth_weight = pregnancy_folder.birth_weight_2
		release_weight = pregnancy_folder.release_weight_2
		birth_date = pregnancy_folder.birth_datetime_2
		release_date = pregnancy_folder.release_date_2
		gender = pregnancy_folder.gender_2

	elif child == "thirdchild":
		weight_field = "weight_of_the_day_3"
		birth_weight = pregnancy_folder.birth_weight_3
		release_weight = pregnancy_folder.release_weight_3
		birth_date = pregnancy_folder.birth_datetime_3
		release_date = pregnancy_folder.release_date_3
		gender = pregnancy_folder.gender_3

	if gender == 'Boy':
		colors = ['#7cd6fd', '#6c7680']
	elif gender == 'Girl':
		colors = ['#ff538d', '#6c7680']
	else:
		colors = ['#fde47c', '#6c7680']

	ep_weights = frappe.get_all("Early Postnatal Consultation", filters={"pregnancy_folder": pregnancy}, fields=["consultation_date", weight_field])

	newborn_weight = []

	if pregnancy_folder.date_time is not None and birth_weight is not None:
		newborn_weight.append({'date': birth_date, 'weight': birth_weight})

	if pregnancy_folder.release_date is not None and release_weight is not None:
		newborn_weight.append({'date': get_datetime(release_date), 'weight': release_weight})

	for ep_weight in ep_weights:
		if ep_weight[weight_field] is not None and ep_weight[weight_field]!=0 and isinstance(ep_weight[weight_field], int):
			newborn_weight.append({'date': get_datetime(ep_weight.consultation_date), 'weight': ep_weight[weight_field]})


	newborn_weight = sorted(newborn_weight, key=lambda x: x["date"])

	titles = []
	values = []
	tenpercents = []

	tenpercentvalue = birth_weight * 0.9

	for nw in newborn_weight:
		titles.append(formatdate(nw["date"]))
		values.append(nw["weight"])
		tenpercents.append(tenpercentvalue)

	data = {
		'labels': titles,
		'datasets': [{
			'values': values
			},
			{
			'title': _('10% Curve'),
			'values': tenpercents
			}]
		}

	return data, colors
