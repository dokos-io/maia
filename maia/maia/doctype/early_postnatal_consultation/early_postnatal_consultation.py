# -*- coding: utf-8 -*-
# Copyright (c) 2019, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from maia.maia_accounting.invoicing import ConsultationController
from frappe.utils import get_datetime

class EarlyPostnatalConsultation(ConsultationController):
	pass

@frappe.whitelist()
def get_last_weight(consultation, pregnancy, child):

	pregnancy_folder = frappe.get_doc("Pregnancy", pregnancy)

	if child == "firstchild":
		weight_field = "weight_of_the_day"
		birth_weight = pregnancy_folder.birth_weight
		release_weight = pregnancy_folder.release_weight
		birth_date = pregnancy_folder.date_time
		release_date = pregnancy_folder.release_date

	elif child == "secondchild":
		weight_field = "weight_of_the_day_2"
		birth_weight = pregnancy_folder.birth_weight_2
		release_weight = pregnancy_folder.release_weight_2
		birth_date = pregnancy_folder.birth_datetime_2
		release_date = pregnancy_folder.release_date_2

	elif child == "thirdchild":
		weight_field = "weight_of_the_day_3"
		birth_weight = pregnancy_folder.birth_weight_3
		release_weight = pregnancy_folder.release_weight_3
		birth_date = pregnancy_folder.birth_datetime_3
		release_date = pregnancy_folder.release_date_3

	ep_weights = frappe.get_all("Early Postnatal Consultation", filters={"pregnancy_folder": pregnancy}, \
		fields=["name", "consultation_date", weight_field])

	dates = []
	dates.append({birth_date: birth_weight})
	dates.append({get_datetime(release_date): release_weight})

	for ep_weight in ep_weights:
		if ep_weight[weight_field] is not None and ep_weight[weight_field]!=0 and isinstance(ep_weight[weight_field], int) \
			and ep_weight.name != consultation:
			dates.append({get_datetime(ep_weight.consultation_date): ep_weight[weight_field]})

	latest_date = max(dates)

	return latest_date.values()
