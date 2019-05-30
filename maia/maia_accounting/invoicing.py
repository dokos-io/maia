# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt
from maia.maia_accounting.doctype.payment.payment import get_payment

class ConsultationController(Document):
	def on_submit(self):
		self.create_and_submit_invoice()

	def validate(self):
		self.check_folder_and_record()

	def check_folder_and_record(self):
		folders_dict = {
			"pregnancy_folder": "Pregnancy",
			"prenatal_interview_folder": "Prenatal Interview",
			"perineum_rehabilitation_folder": "Perineum Rehabilitation",
			"gynecological_folder": "Gynecology"
		}

		if self.is_new():
			for d in folders_dict:
				if getattr(self, d, None):
					v = frappe.db.get_value(folders_dict[d], getattr(self, d), "patient_record")
					if v != self.patient_record:
						frappe.throw(_("This {0} folder don't belong to this patient".format(folders_dict[d].lower())))


	def create_and_submit_invoice(self):
		if not frappe.db.exists("Party", dict(is_social_security=1)):
			self.create_social_security_party()

		if self.third_party_payment == 1 and (self.patient_price == 0 or self.patient_price is None) :
			self.update_invoice_details("Social Security", "third_party_only")

		elif self.third_party_payment == 1 and (self.patient_price != 0 or self.patient_price is not None) :
			self.update_invoice_details("Social Security", "third_party_and_patient")
			self.update_invoice_details("Consultation", "third_party_and_patient")

		else:
			self.update_invoice_details("Consultation", "patient_only")

	def create_social_security_party(self):
		if frappe.db.exists("Party", "CPAM"):
			frappe.db.set_value("Party", "CPAM", "is_social_security", 1)
		else:
			frappe.get_doc({
				"doctype": "Party",
				"party_name": "CPAM",
				"is_social_security": 1
			}).insert(ignore_permissions=True)

	def get_accounting_item(self):
		self.accounting_item = frappe.db.get_value("Accounting Item", dict(code_2035="AA"), "name")

	def update_invoice_details(self, revenue_type, case):
		self.revenue_doc = frappe.new_doc('Revenue')
		self.get_accounting_item()

		customer = frappe.get_doc("Party", dict(is_social_security=1))

		self.revenue_doc.update({
			"revenue_type": revenue_type,
			"practitioner": self.practitioner,
			"patient": self.patient_name,
			"party": customer.name if revenue_type == "Social Security" else None,
			"transaction_date": self.consultation_date,
			"with_items": 1,
			"accounting_item": self.accounting_item,
			"consultation_type": self.doctype,
			"consultation": self.name,
			"codifications": []
		})

		self.add_codification_items(revenue_type, case)

	def add_codification_items(self, revenue_type, case):
		data = {
			self.lump_sum_travel_allowance_codification: self.lump_sum_travel_allowance_value,
			self.sundays_holidays_allowance_codification: self.sundays_holidays_allowance_value,
			self.night_work_allowance_codification: self.night_work_allowance_value,
			self.mileage_allowance_codification: self.mileage_allowance_value
		}

		for codification in self.codification:
			price_field = "basic_price" if self.third_party_payment == 1 else "billing_price"
			data[codification.codification] = frappe.db.get_value("Codification", codification.codification, price_field)	

		if not (case == "third_party_and_patient" and revenue_type != "Social Security"):
			if self.third_party_payment == 1 and self.malady == 1:
				if self.normal_rate:
					for d in data:
						if d != "" and d != 0 and d is not None and d != "HN":
							self.revenue_doc.append("codifications", {
								"codification": d,
								"qty": 1,
								"unit_price": data[d] * 0.7,
								"accounting_item": self.accounting_item
							})

				elif self.alsace_moselle_rate:
					for d in data:
						if d != "" and d != 0 and d is not None and d != "HN":
							self.revenue_doc.append("codifications", {
								"codification": d,
								"qty": 1,
								"unit_price": data[d] * 0.9,
								"accounting_item": self.accounting_item
							})

			else:
				for d in data:
					if d != "" and d != 0 and d is not None and d != "HN":
						self.revenue_doc.append("codifications", {
							"codification": d,
							"qty": 1,
							"unit_price": data[d],
							"accounting_item": self.accounting_item
						})

			if self.mileage_allowance_codification != "" and self.mileage_allowance_codification != 0 and self.mileage_allowance_codification is not None:
				self.revenue_doc.append("codifications", {
					"codification": self.mileage_allowance_codification,
					"qty": self.number_of_kilometers,
					"accounting_item": self.accounting_item
				})

		if not (case == "third_party_and_patient" and revenue_type == "Social Security"):
			if self.third_party_payment == 1 and self.malady == 1:
				if self.normal_rate:
					for d in data:
						if d != "" and d != 0 and d is not None and d != "HN":
							self.revenue_doc.append("codifications", {
								"codification": d,
								"qty": 1,
								"unit_price": data[d] * 0.3,
								"accounting_item": self.accounting_item
							})

				elif self.alsace_moselle_rate:
					for d in data:
						if d != "" and d != 0 and d is not None and d != "HN":
							self.revenue_doc.append("codifications", {
								"codification": d,
								"qty": 1,
								"unit_price": data[d] * 0.1,
								"accounting_item": self.accounting_item
							})

			if self.without_codification != 0 and self.without_codification is not None:
				if not frappe.db.exists("Codification", "HN"):
					frappe.throw(_("Codification HN is missing. Please add it in your codifications list."))

				else:
					self.revenue_doc.append("codifications", {
						"codification": "HN",
						"qty": 1,
						"unit_price": self.without_codification,
						"description": self.without_codification_description,
						"accounting_item": self.accounting_item
					})

			if self.overpayment_value != 0 and self.overpayment_value is not None:
				if not self.codification_description:
					codification_description = frappe.db.get_value("Codification", self.codification, "codification_description")
				else:
					codification_description = self.codification_description
				self.revenue_doc.append("codifications", {
					"codification": self.codification,
					"qty": 1,
					"unit_price": self.overpayment_value,
					"description": _("Overpayment:")+ " " + codification_description,
					"accounting_item": self.accounting_item
				})


		self.revenue_doc.insert()
		self.revenue_doc.submit()

		if not (case == "third_party_and_patient" and revenue_type == "Social Security") and self.paid_immediately == 1:
			if self.revenue_doc:
				payment = get_payment(self.revenue_doc.doctype, self.revenue_doc.name)
				payment.payment_method = self.mode_of_payment
				payment.payment_reference = self.reference
				payment.payment_date = self.consultation_date

				payment.insert()
				payment.submit()

	def on_cancel(self):
		linked_invoices = frappe.get_all("Revenue", filters={"consultation_type": self.doctype, "consultation": self.name, "docstatus": 1})

		for invoice in linked_invoices:
			undo_payment(invoice.name)
			cancel_invoice(invoice.name)

def undo_payment(invoice):
	outstanding = frappe.db.get_value("Revenue", invoice, "outstanding_amount")
	total = frappe.db.get_value("Revenue", invoice, "amount")
	if flt(outstanding) < flt(total):
		payments = frappe.get_all("Payment References", filters={"reference_type": "Revenue", "reference_name": invoice}, fields=["parent"])

		if payments:
			for p in payments:
				doc = frappe.get_doc("Payment", p.parent)
				if doc.docstatus == 1:
					doc.cancel()

			frappe.msgprint(_("A payment linked to this consultation has been cancelled"))

def cancel_invoice(invoice):
	try:
		frappe.get_doc("Revenue", invoice).cancel()
		frappe.db.commit()
	except Exception:
		frappe.db.rollback()
