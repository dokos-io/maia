# Copyright (c) 2019, DOKOS and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, today
from frappe import _

def update_patient_birthday():
	patients = frappe.get_all("Patient Record", fields=["name", "patient_date_of_birth", "patient_age", "spouse_date_of_birth", "spouse_age", "owner"])

	for patient in patients:
		frappe.local.lang = frappe.db.get_value("User", patient.owner, "language")

		if patient.patient_date_of_birth:
			patient_calculated_age = _calculate_age(getdate(patient.patient_date_of_birth))
			if not patient.patient_age or int(patient.patient_age[:2]) != int(patient_calculated_age):
				value = str(patient_calculated_age) + " " + _("Years Old")
				frappe.db.set_value("Patient Record", patient.name, "patient_age", value, modified=False)

		if patient.spouse_date_of_birth:
			spouse_calculated_age = _calculate_age(getdate(patient.spouse_date_of_birth))
			if not patient.spouse_age or int(patient.spouse_age[:2]) != int(spouse_calculated_age):
				value = str(spouse_calculated_age) + " " + _("Years Old")
				frappe.db.set_value("Patient Record", patient.name, "spouse_age", value, modified=False)

def _calculate_age(birthdate):
	nowday = getdate(today())
	return nowday.year - birthdate.year - ((nowday.month, nowday.day) < (birthdate.month, birthdate.day))
