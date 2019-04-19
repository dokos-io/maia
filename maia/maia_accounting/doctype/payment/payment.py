# -*- coding: utf-8 -*-
# Copyright (c) 2019, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
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

	def on_cancel(self):
		self.reverse_gl_entries()

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

	def get_rev_exp_accounting_journal(self, accounting_item):
		journal = frappe.db.get_value("Accounting Item", accounting_item, "accounting_journal")

		if journal:
			return journal
		else:
			frappe.throw(_("Please choose an accounting journal for accounting item {0}".format(accounting_item)))

	def get_bank_cash_accounting_journal(self):
		journal = frappe.db.get_value("Payment Method", self.payment_method, "accounting_journal")

		if journal:
			return journal
		else:
			frappe.throw(_("Please choose an accounting journal for payment method {0}".format(self.payment_method)))

	def get_party_accounting_item(self):
		if self.party_type == "Patient Record" and self.party:
			if frappe.db.exists("Accounting Item", dict(accounting_item_type="Sales Party")):
				party_item = frappe.get_doc("Accounting Item", dict(accounting_item_type="Sales Party"))
			else:
				frappe.throw(_("Please add at least one accounting item with accounting item type as Sales Party"))

		elif self.party_type == "Party" and self.party:
			party_type = "Sales Party" if frappe.db.get_value("Party", self.party, "is_customer") == 1 else "Purchase Party"
			if frappe.db.exists("Accounting Item", dict(accounting_item_type=party_type)):
				party_item = frappe.get_doc("Accounting Item", dict(accounting_item_type=party_type))
			else:
				frappe.throw(_("Please add at least one accounting item with accounting item type as {0}".format(party_type)))

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
			gl_entries.extend(self.get_gl_entries(doc))

		make_gl_entries(gl_entries)

	def get_gl_entries(self, doc):
		entries = []
		if doc.with_items:
			items = doc.get("codifications") if doc.doctype == "Revenue" else doc.get("expense_items")
			for item in items:
				entries.append({
					"posting_date": self.payment_date,
					"accounting_item": item.accounting_item,
					"debit": item.total_amount if self.payment_type == "Outgoing payment" else 0,
					"credit": item.total_amount if self.payment_type == "Incoming payment" else 0,
					"currency": "EUR",
					"reference_type": doc.doctype,
					"reference_name": doc.name,
					"link_doctype": self.doctype,
					"link_docname": self.name,
					"accounting_journal": self.get_rev_exp_accounting_journal(item.accounting_item),
					"practitioner": self.practitioner
				})
		else:
			entries.append({
				"posting_date": self.payment_date,
				"accounting_item": doc.accounting_item,
				"debit": doc.amount if self.payment_type == "Outgoing payment" else 0,
				"credit": doc.amount if self.payment_type == "Incoming payment" else 0,
				"currency": "EUR",
				"reference_type": doc.doctype,
				"reference_name": doc.name,
				"link_doctype": self.doctype,
				"link_docname": self.name,
				"accounting_journal": self.get_rev_exp_accounting_journal(item.accounting_item),
				"practitioner": self.practitioner
			})

		return entries
	
	def make_pending_gl_entries(self):
		if self.pending_amount > 0:
			if not self.party:
				frappe.throw(_("Please select a party if the paid amount is not fully allocated"))

			accounting_item = self.get_party_accounting_item()
			gl_entries = []

			gl_entries.append({
				"posting_date": self.payment_date,
				"accounting_item": accounting_item,
				"debit": self.pending_amount if self.payment_type == "Outgoing payment" else 0,
				"credit": self.pending_amount if self.payment_type == "Incoming payment" else 0,
				"currency": "EUR",
				"reference_type": self.doctype,
				"reference_name": self.name,
				"link_doctype": self.doctype,
				"link_docname": self.name,
				"accounting_journal": self.get_rev_exp_accounting_journal(item.accounting_item),
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
			"reference_type": self.doctype,
			"reference_name": self.name,
			"link_doctype": self.doctype,
			"link_docname": self.name,
			"accounting_journal": self.get_bank_cash_accounting_journal(),
			"practitioner": self.practitioner
		})

		make_gl_entries(gl_entries)

	def set_outstanding_amount(self):
		for ref in self.get("payment_references"):
			outstanding = frappe.db.get_value(ref.reference_type, ref.reference_name, "outstanding_amount")
			frappe.db.set_value(ref.reference_type, ref.reference_name, "outstanding_amount", flt(outstanding) - flt(ref.paid_amount))

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