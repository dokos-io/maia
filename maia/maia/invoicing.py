# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, flt
from frappe import _
import time
from frappe.model.document import Document
from erpnext.accounts.doctype.payment_request.payment_request import make_payment_request, make_payment_entry
from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_sales_return

def create_and_submit_invoice(self):

	if not frappe.db.exists("Customer", dict(customer_name="CPAM")):
		create_social_security_customer(self)

	if self.third_party_payment == 1 and (self.patient_price == 0 or self.patient_price is None) :
		customer = frappe.get_doc("Customer", dict(customer_name="CPAM"))
		update_invoice_details(self, customer.name, "third_party_only")

	elif self.third_party_payment == 1 and (self.patient_price != 0 or self.patient_price is not None) :
		customer = frappe.get_doc("Customer", dict(customer_name="CPAM"))
		update_invoice_details(self, customer.name, "third_party_and_patient")

		update_invoice_details(self, self.customer, "third_party_and_patient")

	else:
		update_invoice_details(self, self.customer, "patient_only")

def create_social_security_customer(doc):
	customer =  frappe.get_doc({
		"doctype": "Customer",
		"customer_name": "CPAM",
		"customer_type": "Company",
		"customer_group": _("Government"),
		"territory": _("All Territories")
	}).insert(ignore_permissions=True)


def get_customer_name(self):
	customer_name = frappe.db.get_value("Patient Record", self.patient_record, "customer")
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

	terms = frappe.db.get_value("Terms and Conditions", "Termes et Conditions Standard", "terms")

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
		"terms": terms,
		"items": []
	})


	if not (case == "third_party_and_patient" and customer != "CPAM"):
		data = {self.codification: self.codification_value, self.lump_sum_travel_allowance_codification: self.lump_sum_travel_allowance_value, self.sundays_holidays_allowance_codification: self.sundays_holidays_allowance_value, self.night_work_allowance_codification: self.night_work_allowance_value, self.mileage_allowance_codification: self.mileage_allowance_value}
		if self.third_party_payment == 1 and self.malady == 1:
			if self.normal_rate:
				for d in data:
					if d != "" and d != 0 and d is not None and d != "HN":
						invoice.append("items", {
							"item_code": d,
							"qty": 1,
							"rate": data[d] * 0.7
						})

			elif self.alsace_moselle_rate:
				for d in data:
					if d != "" and d != 0 and d is not None and d != "HN":
						invoice.append("items", {
							"item_code": d,
							"qty": 1,
							"rate": data[d] * 0.9
						})

		else:
			for d in data:
				if d != "" and d != 0 and d is not None and d != "HN":
					invoice.append("items", {
						"item_code": d,
						"qty": 1,
					})

		if self.mileage_allowance_codification != "" and self.mileage_allowance_codification != 0 and self.mileage_allowance_codification is not None:
			invoice.append("items", {
				"item_code": self.mileage_allowance_codification,
				"qty": self.number_of_kilometers,
			})

	if not (case == "third_party_and_patient" and customer == "CPAM"):
		if self.third_party_payment == 1 and self.malady == 1:
			data = {self.codification: self.codification_value, self.lump_sum_travel_allowance_codification: self.lump_sum_travel_allowance_value, self.sundays_holidays_allowance_codification: self.sundays_holidays_allowance_value, self.night_work_allowance_codification: self.night_work_allowance_value, self.mileage_allowance_codification: self.mileage_allowance_value}
			if self.normal_rate:
				for d in data:
					if d != "" and d != 0 and d is not None and d != "HN":
						invoice.append("items", {
							"item_code": d,
							"qty": 1,
							"rate": data[d] * 0.3
						})

			elif self.alsace_moselle_rate:
				for d in data:
					if d != "" and d != 0 and d is not None and d != "HN":
						invoice.append("items", {
							"item_code": d,
							"qty": 1,
							"rate": data[d] * 0.1
						})

		if self.without_codification != 0 and self.without_codification is not None:
			if not frappe.db.exists("Codification", "HN"):
				frappe.throw(_("Codification HN is missing. Please add it in your codifications list."))

			else:
				invoice.append("items", {
					"item_code": "HN",
					"qty": 1,
					"rate": self.without_codification,
					"description": self.without_codification_description
				})

		if self.overpayment_value != 0 and self.overpayment_value is not None:
			if not self.codification_description:
				codification_description = frappe.db.get_value("Codification", self.codification, "codification_description")
			else:
				codification_description = self.codification_description
			invoice.append("items", {
				"item_code": self.codification,
				"qty": 1,
				"rate": self.overpayment_value,
				"description": _("Overpayment:")+ " " + codification_description
			})

	invoice.set_missing_values()
	invoice.insert()
	invoice.submit()


	if customer == "CPAM":
		frappe.db.set_value(self.doctype, self.name, "social_security_invoice", invoice.name)
	else:
		frappe.db.set_value(self.doctype, self.name, "invoice", invoice.name)
	self.reload()


	if not (case == "third_party_and_patient" and customer == "CPAM") and self.paid_immediately == 1:
		payment_request = make_payment_request(dt="Sales Invoice", dn=invoice.name, submit_doc=True, mute_email=True)
		payment_entry = frappe.get_doc(make_payment_entry(payment_request.name))

		payment_entry.mode_of_payment = self.mode_of_payment
		payment_entry.reference_no = self.reference
		payment_entry.reference_date = self.consultation_date
		payment_entry.posting_date = frappe.flags.current_date

		payment_entry.submit()

def cancel_consultation_and_invoice(self):
	if self.invoice is not None:
		undo_payment(self.invoice)
		make_return(self.invoice)

	if self.social_security_invoice is not None:
		undo_payment(self.social_security_invoice)
		make_return(self.social_security_invoice)

def undo_payment(invoice):
	outstanding = frappe.db.get_value("Sales Invoice", invoice, "outstanding_amount")
	total = frappe.db.get_value("Sales Invoice", invoice, "grand_total")
	if flt(outstanding) < flt(total):
		payments = frappe.get_all("Payment Entry Reference", filters={"reference_doctype": "Sales Invoice", "reference_name": invoice}, fields=["parent"])

		if payments:
			for p in payments:
				doc = frappe.get_doc("Payment Entry", p.parent)
				if doc.docstatus == 1:
					doc.cancel()

			frappe.msgprint(_("A payment linked to this consultation has been cancelled"))

def make_return(invoice):
	try:
		rt = make_sales_return(invoice)
		rt.insert()
		rt.submit()
		frappe.db.commit()
	except Exception:
		frappe.db.rollback()

def remove_cancelled_invoice(self):
	if self.invoice is not None:
		self.invoice = None

	if self.social_security_invoice is not None:
		self.social_security_invoice = None
