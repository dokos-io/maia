# -*- coding: utf-8 -*-
# Copyright (c) 2018, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt
from maia.maia_accounting.doctype.payment.payment import get_payment, get_replaced_practitioner

class ConsultationController(Document):
	def on_submit(self):
		if not self.accounting_disabled:
			self.create_and_submit_invoice()

	def validate(self):
		self.check_folder_and_record()
		self.validate_third_party_payment_options()
		self.validate_pricing()

	def validate_third_party_payment_options(self):
		if self.third_party_payment and not self.accounting_disabled:
			if not self.hundred_percent_maternity and not self.malady:
				frappe.throw(_("You need to select 100% maternity or malady if you want a third party payment"))

			if self.malady:
				if not self.normal_rate and not self.alsace_moselle_rate:
					frappe.throw(_("You need to select a rate for a malady third party payment"))

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

	def validate_pricing(self):
		self.clear_table()
		self.add_codifications()
		self.add_without_codifications()
		self.add_allowances()
		self.refresh_totals()

	def clear_table(self):
		self.consultation_items = []

	def add_codifications(self):
		for codification in self.codification:
			result = self.calculate_values(codification.codification, "codification")
			self.append("consultation_items", result)

	def add_without_codifications(self):
		if self.without_codification:
			price = self.without_codification
			result = self.calculate_values("HN", "without_codification", price, price, True)
			self.append("consultation_items", result)

	def add_allowances(self):
		self.add_sundays_allowance()
		self.add_lump_sum_travel_allowance()
		self.add_night_work_allowance()
		self.add_mileage_allowance()

	def add_sundays_allowance(self):
		if self.sundays_holidays_allowance:
			self.add_allowance("sundays_holidays_allowance")

	def add_lump_sum_travel_allowance(self):
		if self.lump_sum_travel_allowance:
			self.add_allowance("lump_sum_travel_allowance")

	def add_night_work_allowance(self):
		if self.night_work_allowance:
			filter_name = "night_work_allowance_1" if self.night_work_allowance_type == "20h-0h | 6h-8h" else "night_work_allowance_2";
			self.add_allowance(filter_name)

	def add_mileage_allowance(self):
		if self.mileage_allowance:
			filter_name = "mileage_allowance_lowland" if self.mileage_allowance_type == "Lowland" else \
				("mileage_allowance_mountain" if self.mileage_allowance_type == "Mountain" else "mileage_allowance_walking_skiing")
			km_coef = self.number_of_kilometers or 0
			self.add_allowance(filter_name, km_coef)

	def add_allowance(self, allowance_type, rate_coef=1):
		allowance_list = frappe.db.get_list("Codification", filters={allowance_type: 1}, fields=["name", "codification", "basic_price", "billing_price"])
		if allowance_list:
			basic_price = allowance_list[0].basic_price * rate_coef
			billing_price = allowance_list[0].billing_price * rate_coef
			result = self.calculate_values(allowance_list[0].name, "allowance", basic_price, billing_price, True)
			self.append("consultation_items", result)

	def calculate_values(self, codification, category, basic_price=0, billing_price=0, force_rate=False):
		result = frappe.db.get_value("Codification", codification, ["name", "codification", "codification_description",
				"basic_price", "billing_price", "accounting_item"], as_dict=True)
		print(result)
		split = self.calculate_split(result, category, basic_price, billing_price, force_rate)
		print(split)
		return split

	def calculate_split(self, values, category, basic_price=0, billing_price=0, force_rate=False):
		obj = {
			"codification_name": values["name"],
			"codification": values["codification"],
			"description": values["codification_description"],
			"rate": billing_price if force_rate else values["basic_price"],
			"social_security_share": 0,
			"patient_share": billing_price if force_rate else (values["basic_price"] if self.social_security_price else values["billing_price"]),
			"overbilling": 0,
			"category": category
		}

		obj["overbilling"] = 0 if self.social_security_price else ((billing_price - basic_price) if force_rate else (values["billing_price"] - values["basic_price"]))

		if category != "without_codification":
			if self.third_party_payment and self.hundred_percent_maternity:
				obj["rate"] = billing_price if force_rate else values["basic_price"]
				obj["social_security_share"] = basic_price if force_rate else values["basic_price"]
				obj["patient_share"] = obj["overbilling"]
		
			if self.third_party_payment and self.malady and self.normal_rate:
				obj["rate"] = (basic_price if force_rate else values["basic_price"]) if self.social_security_price else (billing_price if force_rate else values["basic_price"])
				obj["social_security_share"] = flt(obj["rate"]) * 0.7
				obj["patient_share"] = flt(obj["rate"]) * 0.3 + obj["overbilling"]

			if self.third_party_payment and self.malady and self.alsace_moselle_rate:
				obj["rate"] = (basic_price if force_rate else values["basic_price"]) if self.social_security_price else (billing_price if force_rate else values["basic_price"])
				obj["social_security_share"] = flt(obj["rate"]) * 0.9
				obj["patient_share"] = flt(obj["rate"]) * 0.1 + obj["overbilling"]

		return obj

	def refresh_totals(self):
		patient_price = 0
		social_security_share=0
		total_price = 0
		overbilling = 0
		without_codification = 0
		allowances = 0
		codifications = 0

		for item in self.consultation_items:
			total_price += item.rate + item.overbilling
			patient_price += item.patient_share
			social_security_share += item.social_security_share
			overbilling += item.overbilling

			if item.category == "without_codification":
				without_codification += item.rate
			elif item.category == "allowance":
				allowances += item.rate
			elif item.category == "codification":
				codifications += item.rate

		self.codification_value = codifications if codifications > 0 else 0
		self.cpam_share_display = social_security_share if social_security_share > 0 else 0
		self.patient_price = patient_price if patient_price > 0 else 0
		self.total_price = total_price if total_price > 0 else 0
		self.overpayment_value = overbilling if overbilling > 0 else 0
		self.without_codification_display = without_codification if without_codification > 0 else 0
		self.total_allowances = allowances if allowances > 0 else 0

	def create_and_submit_invoice(self):
		if not frappe.db.exists("Party", dict(is_social_security=1)):
			self.create_social_security_party()

		self.accounted_practitioner = self.practitioner
		replaced_practitioner = get_replaced_practitioner(self.consultation_date, self.practitioner)
		if replaced_practitioner:
			self.accounted_practitioner = replaced_practitioner

		if self.third_party_payment == 1 and not self.patient_price:
			self.update_invoice_details("Social Security")

		elif self.third_party_payment == 1 and self.patient_price > 0:
			self.update_invoice_details("Social Security")
			self.update_invoice_details("Consultation")

		else:
			self.update_invoice_details("Consultation")

	def create_social_security_party(self):
		if frappe.db.exists("Party", "CPAM"):
			frappe.db.set_value("Party", "CPAM", "is_social_security", 1)
		else:
			frappe.get_doc({
				"doctype": "Party",
				"party_name": "CPAM",
				"is_social_security": 1
			}).insert(ignore_permissions=True)

	def update_invoice_details(self, revenue_type):
		self.revenue_doc = frappe.new_doc('Revenue')
		customer = frappe.get_doc("Party", dict(is_social_security=1))

		self.revenue_doc.update({
			"revenue_type": revenue_type,
			"practitioner": self.accounted_practitioner,
			"patient": self.patient_name,
			"party": customer.name if revenue_type == "Social Security" else None,
			"transaction_date": self.consultation_date,
			"with_items": 1,
			"consultation_type": self.doctype,
			"consultation": self.name,
			"codifications": []
		})

		self.add_codification_items(revenue_type)
		self.revenue_doc.insert()
		self.revenue_doc.submit()

		if revenue_type == "Consultation" and self.paid_immediately == 1:
			if self.revenue_doc:
				payment = get_payment(self.revenue_doc.doctype, self.revenue_doc.name)
				payment.practitioner = self.accounted_practitioner
				payment.payment_method = self.mode_of_payment
				payment.payment_reference = self.reference
				payment.payment_date = self.consultation_date

				payment.insert()
				payment.submit()

	def add_codification_items(self, revenue_type):
		for item in self.consultation_items:
			if revenue_type == "Social Security" and flt(item.social_security_share) == 0:
				continue
			elif revenue_type == "Consultation" and flt(item.patient_share) == 0:
				continue

			invoicing_object = {
				"codification": item.codification_name,
				"qty": 1,
				"unit_price": flt(item.social_security_share) if revenue_type == "Social Security" else flt(item.patient_share),
				"description": item.description,
				"accounting_item": frappe.db.get_value("Codification", item.codification_name, "accounting_item")
			}

			if invoicing_object:
				self.revenue_doc.append("codifications", invoicing_object)

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
