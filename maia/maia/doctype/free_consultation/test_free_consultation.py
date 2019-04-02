# -*- coding: utf-8 -*-
# Copyright (c) 2015, DOKOS and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
from maia.maia.doctype.free_consultation.free_consultation import create_and_submit_invoice, get_customer_name

test_records = frappe.get_test_records('Free Consultation')

class TestFreeConsultation(unittest.TestCase):
	def test_create_and_submit_invoice(self):
		"""
		Four Test Cases Needed
		"""
		consultations = []
		consultation_1 = create_free_consultation(0, "20")
		consultations.append(consultation_1)

		consultation_2 = create_free_consultation(1, "20")
		consultations.append(consultation_2)

		consultation_3 = create_free_consultation(1, "0")
		consultations.append(consultation_3)

		for c in consultations:
			print(c.name)
			c.save()
			self.assertEquals(c.patient_name, "_Test Patient1")
		
			create_and_submit_invoice(c)
			if c == consultation_1 or c == consultation_2:
				si = frappe.get_doc("Sales Invoice", c.invoice)
				self.assertEquals(si.status, "Unpaid")

			elif c == consultation_3:
				si = frappe.get_doc("Sales Invoice", c.social_security_invoice)
				self.assertEquals(si.status, "Paid")
				

def create_free_consultation(third_party_payment, without_codification):       
	consultation = frappe.get_doc({
		"doctype": "Free Consultation",
		"patient_record": "_Test Patient1",
		"practitioner": "_Test Practicioner",
		"consultation_date": "2017-07-05",
		"lump_sum_travel_allowance": 1,
		"codification": "_Test Cod",
		"customer": "_Test Patient1",
		"without_codification": without_codification,
		"third_party_payment": third_party_payment
	})
	consultation.insert()

	return consultation
