# -*- coding: utf-8 -*-
# Copyright (c) 2017, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json

@frappe.whitelist()
def get_pregnancies(obj):
    obj = frappe._dict(json.loads(obj))

    patient_record = obj.selected_patient_record
    pregnancies = []
    patient = frappe.get_doc("Patient Record", patient_record)

    past_pregnancies = frappe.db.sql(
        """SELECT * FROM `tabObstetrical Background` WHERE parent='{0}'""".format(patient_record), as_dict=True)

    for past_pregnancy in past_pregnancies:
        past_pregnancy["data_type"]="past_pregnancy"
        pregnancies.append(past_pregnancy)

    current_pregnancies = frappe.db.sql(
        """SELECT * FROM `tabPregnancy` WHERE patient_record='{0}'""".format(patient_record), as_dict=True)

    for current_pregnancy in current_pregnancies:
        current_pregnancy["data_type"]="current_pregnancy"
        pregnancies.append(current_pregnancy)

    return pregnancies
