# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate
from frappe import _
import time
from frappe.model.document import Document
from erpnext.accounts.doctype.payment_request.payment_request import make_payment_request, make_payment_entry

def create_and_submit_invoice(self):

	if frappe.db.get_value("Customer", {"customer_name": "CPAM"}) is None:
					create_social_security_customer(self)

	if self.third_party_payment == 1 and (self.without_codification == 0 or self.without_codification is None) :
					customer = frappe.db.get_value("Customer", {"customer_name": "CPAM"})
					update_invoice_details(self, customer, "third_party_only")

	elif self.third_party_payment == 1 and (self.without_codification != 0 or self.without_codification is not None) :
					customer = frappe.db.get_value("Customer", {"customer_name": "CPAM"})
					update_invoice_details(self, customer, "third_party_and_patient")

					customer = self.customer
					update_invoice_details(self, customer, "third_party_and_patient")

	else:
					customer = self.customer
					update_invoice_details(self, customer, "patient_only")

def create_social_security_customer(doc):
	customer =  frappe.get_doc({
					"doctype": "Customer",
					"customer_name": "CPAM",
					"customer_type": "Company",
					"customer_group": _("Government"),
					"territory": _("All Territories")
	}).insert(ignore_permissions=True)


def get_customer_name(self):
	customer_name = frappe.db.get_value("Customer", {"patient_record": self.patient_record})
	frappe.db.set_value(self.doctype, self.name, "customer", customer_name)

	self.reload()


def update_invoice_details(self, customer, case):
	invoice = frappe.new_doc('Sales Invoice')
	company = frappe.get_value("Professional Information Card", self.practitioner, "company")

	if customer == "CPAM":
					selling_price_list = "CPAM"
	else:
					selling_price_list = "Sage Femme"

	if self.no_teletransmission == 1:
					teletransmission = 0
	else:
					teletransmission = 1


	invoice.update({
					"customer": customer,
					"company": company,
					"set_posting_time": 1,
					"posting_date": self.consultation_date,
					"due_date": self.consultation_date,
					"patient_record": self.patient_record,
					"selling_price_list": selling_price_list,
					"teletransmission": teletransmission,
					"consultation_reference": self.name,
					"tc_name": "Termes et Conditions Standard",
					"items": []
	})


	if case == "third_party_and_patient" and customer != "CPAM":
					pass
	else:

					data = [self.codification, self.lump_sum_travel_allowance_codification, self.sundays_holidays_allowance_codification, self.night_work_allowance_codification]
					for d in data:
									if d != "" and d != 0 and d is not None and d != "HN":
													invoice.append("items", {
																	"item_code": d,
																	"qty": 1,
													})

	if case == "third_party_and_patient" and customer != "CPAM":
					pass
	else:
					if self.mileage_allowance_codification != "" and self.mileage_allowance_codification != 0 and self.mileage_allowance_codification is not None:
									invoice.append("items", {
													"item_code": self.mileage_allowance_codification,
													"qty": self.number_of_kilometers,
									})

	if case == "third_party_and_patient" and customer == "CPAM":
					pass
	else:
					if self.without_codification != 0 and self.without_codification is not None:
									if frappe.db.get_value("Codification", {"name": "HN"}) is None:
													hn_missing = _("Codification HN is missing. Please add it in your codifications list.")
													frappe.throw(hn_missing)
									invoice.append("items", {
													"item_code": "HN",
													"qty": 1,
													"rate": self.without_codification,
													"description": self.without_codification_description
									})

	invoice.set_missing_values()

	invoice.insert()

	invoice.submit()


	if customer == "CPAM":
					frappe.db.set_value(self.doctype, self.name, "social_security_invoice", invoice.name)

	else:
					frappe.db.set_value(self.doctype, self.name, "invoice", invoice.name)

	self.reload()


	if case == "third_party_and_patient" and customer == "CPAM":
					pass
	else:
					if self.paid_immediately == 1:

									payment_request = make_payment_request(dt="Sales Invoice", dn=invoice.name, submit_doc=True, mute_email=True)

									payment_entry = frappe.get_doc(make_payment_entry(payment_request.name))

									payment_entry.mode_of_payment = self.mode_of_payment
									payment_entry.reference_no = self.reference
									payment_entry.reference_date = self.consultation_date
									payment_entry.posting_date = frappe.flags.current_date

									payment_entry.submit()



def cancel_consultation_and_invoice(self):
	if self.invoice is not None:
					invoice = frappe.get_doc("Sales Invoice", self.invoice)
					invoice.cancel()

	if self.social_security_invoice is not None:
					ss_invoice = frappe.get_doc("Sales Invoice", self.social_security_invoice)
					ss_invoice.cancel()

def remove_cancelled_invoice(self):
	if self.invoice is not None:
		self.invoice = None

	if self.social_security_invoice is not None:
		self.social_security_invoice = None
