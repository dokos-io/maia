# -*- coding: utf-8 -*-
# Copyright (c) 2017, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.utils import formatdate, format_datetime

@frappe.whitelist()
def get_pregnancies(obj):
    obj = frappe._dict(json.loads(obj))

    patient_record = obj.selected_patient_record
    pregnancies = []
    patient = frappe.get_doc("Patient Record", patient_record)

    in_progress_pregnancies = frappe.db.sql(
        """SELECT * FROM `tabPregnancy` WHERE patient_record='{0}' AND (date_time is NULL or date_time = '') ORDER BY expected_term DESC""".format(patient_record), as_dict=True)

    for in_progress_pregnancy in in_progress_pregnancies:
        in_progress_pregnancy["data_type"] = "current_pregnancy"
        if in_progress_pregnancy["expected_term"]:
            in_progress_pregnancy["expected_term"] = formatdate(in_progress_pregnancy["expected_term"])
        if in_progress_pregnancy["beginning_of_pregnancy"]:
            in_progress_pregnancy["beginning_of_pregnancy"] = formatdate(in_progress_pregnancy["beginning_of_pregnancy"])
        pregnancies.append(in_progress_pregnancy)

    current_pregnancies = frappe.db.sql(
       """SELECT * FROM `tabPregnancy` WHERE patient_record='{0}' AND date_time!='' ORDER BY date_time DESC""".format(patient_record), as_dict=True)

    for current_pregnancy in current_pregnancies:
        current_pregnancy["data_type"] = "current_pregnancy"
        if current_pregnancy["date_time"]:
            current_pregnancy["date_time"] = formatdate(current_pregnancy["date_time"])
        pregnancies.append(current_pregnancy)

    past_pregnancies = frappe.db.sql(
        """SELECT * FROM `tabObstetrical Background` WHERE parent='{0}' ORDER BY date DESC""".format(patient_record), as_dict=True)

    for past_pregnancy in past_pregnancies:
        past_pregnancy["data_type"] = "past_pregnancy"
        if past_pregnancy["date"]:
            past_pregnancy["date"] = formatdate(past_pregnancy["date"])
        pregnancies.append(past_pregnancy)

    return pregnancies
