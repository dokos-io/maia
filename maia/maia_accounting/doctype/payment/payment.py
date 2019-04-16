# -*- coding: utf-8 -*-
# Copyright (c) 2019, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from maia.maia_accounting.controllers.accounting_controller import AccountingController
from frappe.utils import flt
from maia.maia_accounting.doctype.general_ledger_entry.general_ledger_entry import make_gl_entries

class Payment(AccountingController):
	def validate(self):
		self.validate_duplicate_entry()
		self.validate_paid_allocation()
		self.set_title()
		self.set_status()

	def before_submit(self):
		self.validate_paid_allocation()

	def on_submit(self):
		self.post_gl_entries()
		self.set_outstanding_amount()

	def validate_paid_allocation(self):
		total_allocated = 0
		for reference in self.payment_references:
			if reference.paid_amount > reference.outstanding_amount:
				reference.paid_amount = reference.outstanding_amount

			total_allocated += flt(reference.paid_amount)

		self.pending_amount = self.paid_amount - total_allocated

	def validate_duplicate_entry(self):
		reference_names = []
		for d in self.get("payment_references"):
			if (d.reference_type, d.reference_name) in reference_names:
				frappe.throw(_("Row #{0}: Duplicate entry in References {1} {2}")
					.format(d.idx, d.reference_type, d.reference_name))
			reference_names.append((d.reference_type, d.reference_name))

	def get_rev_exp_accounting_journal(self):
		journals = frappe.get_all("Maia Accounting Journal", filters={"journal_type": "Sales journal" \
			if self.payment_type == "Incoming payment" else "Purchase journal"})

		if journals:
			return journals[0].name
		else:
			frappe.throw(_("Please configure your accounting journals first"))

	def get_bank_cash_accounting_journal(self):
		payment_type = frappe.db.get_value("Payment Method", self.payment_method, "payment_type")
		journals = frappe.get_all("Maia Accounting Journal", filters={"journal_type": "Bank journal" \
			if payment_type == "Bank" else "Cash journal"})

		if journals:
			return journals[0].name
		else:
			frappe.throw(_("Please configure your accounting journals first"))

	def get_party_accounting_item(self):
		if self.party_type == "Patient Record" and self.party:
			party_item = frappe.db.get_value("Patient Record", self.party, "accounting_item")
			if not party_item:
				default_item = frappe.get_all("Accounting Item", filters={"accounting_item_type": "Sales Party"})
				if default_item:
					party_item = default_item[0].name

		elif self.party_type == "Party" and self.party:
			party_item = frappe.db.get_value("Party", self.party, ["accounting_item", "is_customer", "is_supplier"])
			if not party_item.accounting_item:
				default_item = frappe.get_all("Accounting Item", filters={"accounting_item_type": "Sales Party" \
					if party_item.is_customer == 1 else "Purchase Party"})
				if default_item:
					party_item = default_item[0].name

		return party_item

	def set_title(self):
		self.title = self.party if self.party_type == "Party" else self.patient

	def post_gl_entries(self):
		self.make_references_gl_entries()
		self.make_pending_gl_entries()
		self.make_payment_gl_entries()

	def make_references_gl_entries(self):
		gl_entries = []
		for ref in self.get("payment_references"):
			doc = frappe.get_doc(ref.reference_type, ref.reference_name)

			if hasattr(doc, "with_items") and doc.with_items:
				for codification in doc.get("codifications"):
					gl_entries.append({
						"posting_date": self.payment_date,
						"accounting_item": codification.accounting_item,
						"debit": codification.total_amount if self.payment_type == "Outgoing payment" else 0,
						"credit": codification.total_amount if self.payment_type == "Incoming payment" else 0,
						"currency": "EUR",
						"reference_type": ref.reference_type,
						"reference_name": ref.reference_name,
						"accounting_journal": self.get_rev_exp_accounting_journal(),
						"practitioner": self.practitioner
					})
				
			else:
				gl_entries.append({
						"posting_date": self.payment_date,
						"accounting_item": doc.accounting_item,
						"debit": doc.amount if self.payment_type == "Outgoing payment" else 0,
						"credit": doc.amount if self.payment_type == "Incoming payment" else 0,
						"currency": "EUR",
						"reference_type": ref.reference_type,
						"reference_name": ref.reference_name,
						"accounting_journal": self.get_rev_exp_accounting_journal(),
						"practitioner": self.practitioner
					})
		make_gl_entries(gl_entries)
	
	def make_pending_gl_entries(self):
		if not self.party:
			frappe.throw(_("Please select a party if the paid amount is not fully allocated"))

		if self.pending_amount > 0:
			accounting_item = self.get_party_accounting_item()
			gl_entries = []

			gl_entries.append({
				"posting_date": self.payment_date,
				"accounting_item": accounting_item,
				"debit": self.pending_amount if self.payment_type == "Outgoing payment" else 0,
				"credit": self.pending_amount if self.payment_type == "Incoming payment" else 0,
				"currency": "EUR",
				"reference_type": "Payment",
				"reference_name": self.name,
				"accounting_journal": self.get_rev_exp_accounting_journal(),
				"practitioner": self.practitioner
			})

			make_gl_entries(gl_entries)

	def make_payment_gl_entries(self):
		gl_entries = []

		bank_account = frappe.db.get_value("Payment Method", self.payment_method, "bank_account")
		account = frappe.db.get_value("Maia Bank Account", bank_account, "accounting_item")

		gl_entries.append({
			"posting_date": self.payment_date,
			"accounting_item": account,
			"debit": self.paid_amount if self.payment_type == "Incoming payment" else 0,
			"credit": self.paid_amount if self.payment_type == "Outgoing payment" else 0,
			"currency": "EUR",
			"reference_type": "Payment",
			"reference_name": self.name,
			"accounting_journal": self.get_bank_cash_accounting_journal(),
			"practitioner": self.practitioner
		})

		make_gl_entries(gl_entries)

	def set_outstanding_amount(self):
		for ref in self.get("payment_references"):
			outstanding = frappe.db.get_value(ref.reference_type, ref.reference_name, "outstanding_amount")
			frappe.db.set_value(ref.reference_type, ref.reference_name, "outstanding_amount", flt(outstanding) + flt(ref.paid_amount))

@frappe.whitelist()
def get_payment(dt, dn):
	source_doc = frappe.get_doc(dt, dn)

	payment = frappe.new_doc("Payment")
	payment.payment_type = "Incoming payment" if dt == "Revenue" else "Outgoing payment"
	payment.party_type = "Party" if source_doc.party else "Patient Record"
	payment.party = source_doc.party if source_doc.party else source_doc.patient
	payment.paid_amount = source_doc.outstanding_amount

	payment.append("payment_references", {
		'reference_type': dt,
		'reference_name': dn,
		'outstanding_amount': source_doc.outstanding_amount,
		'paid_amount': source_doc.outstanding_amount
	})

	return payment

@frappe.whitelist()
def get_outstanding_references(party_type, payment_type, party=None):
	dt = "Revenue" if payment_type == "Incoming payment" else "Expense"

	filters = {"outstanding_amount": [">", 0]}
	if party:
		party_filter = "party" if party_type == "Party" else "patient"
		filters[party_filter] = party

	references = frappe.get_all(dt, filters=filters, fields=["name", "amount", "outstanding_amount"])

	return [dict(r,**{"doctype": dt}) for r in references]