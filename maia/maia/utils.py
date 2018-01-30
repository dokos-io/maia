# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document


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
            elif pregnancy.child_full_name_2 or pregnancy.child_gender_2 or pregnancy.child_weight_2 or pregnancy.child_health_state_2 or pregnancy.feeding_2:
                children += 1
            elif pregnancy.child_full_name_3 or pregnancy.child_gender_3 or pregnancy.child_weight_3 or pregnancy.child_health_state_3 or pregnancy.feeding_3:
                children += 1

            parity += children

    pregnancies = frappe.get_all("Pregnancy", filters={'patient_record': patient_record}, fields=['name', 'date_time', 'twins', 'triplets', 'birth_datetime_2', 'birth_datetime_3'])

    for pregnancy in pregnancies:
        gravidity += 1

        children = 0
        if pregnancy.date_time is not None:
            children += 1

        if pregnancy.twins is not None:
            if pregnancy.birth_datetime_2 is not None:
                children += 1

        elif pregnancy.triplets is not None:
            if pregnancy.birth_datetime_3 is not None:
                children += 1

        parity += children

    return gravidity, parity
