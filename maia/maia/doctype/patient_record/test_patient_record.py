# -*- coding: utf-8 -*-
# Copyright (c) 2017, DOKOS and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest

class TestPatientRecord(unittest.TestCase):
	def test_patient_record(self):
                patient = create_patient_record()


def create_patient_record():
        patient = frappe.get_doc({
                "doctype": "Patient Record",
                "patient_first_name": "_Test",
                "patient_last_name": "Patient"
        })

        patient.insert()

        return patient
