# -*- coding: utf-8 -*-
# Copyright (c) 2019, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import maia
from frappe import _
from maia.maia_accounting.controllers.accounting_controller import AccountingController
from frappe.utils import flt, getdate, formatdate, nowdate
from maia.maia_accounting.doctype.general_ledger_entry.general_ledger_entry import make_gl_entries
from maia.maia_accounting.utils import get_accounting_query_conditions
import json

class Payment(AccountingController):
	def validate(self):
		self.validate_duplicate_entry()
		self.validate_payment_type()
		self.validate_paid_allocation()
		self.set_title()
		self.set_status()

	def before_submit(self):
		self.validate_paid_allocation()

	def on_submit(self):
		self.post_gl_entries()
		self.set_outstanding_amount()

	def on_cancel(self):
		self.update_outstanding_amount()
		self.reverse_gl_entries()

	def on_trash(self):
		frappe.throw(_("Deleting this document is not permitted."))

	def validate_payment_type(self):
		if flt(self.paid_amount) < 0:
			paid_amount = abs(self.paid_amount)
			self.payment_type = "Outgoing payment" if self.payment_type == "Incoming payment" else "Incoming payment"
			self.paid_amount = paid_amount

	def validate_paid_allocation(self):
		total_allocated = 0
		for reference in self.payment_references:
			if not reference.outstanding_amount:
				reference.outstanding_amount = frappe.db.get_value(reference.reference_type, reference.reference_name, "outstanding_amount")
			if abs(reference.paid_amount) > abs(reference.outstanding_amount):
				reference.paid_amount = reference.outstanding_amount

			total_allocated += flt(abs(reference.paid_amount))

		self.pending_amount = (flt(self.paid_amount) + flt(self.previously_paid_amount)) - total_allocated

	def validate_duplicate_entry(self):
		reference_names = []
		for d in self.get("payment_references"):
			if (d.reference_type, d.reference_name) in reference_names:
				frappe.throw(_("Row #{0}: Duplicate entry in References {1} {2}")
					.format(d.idx, d.reference_type, d.reference_name))
			reference_names.append((d.reference_type, d.reference_name))

	def update_outstanding_amount(self):
		for reference in self.payment_references:
			outstanding_amount = frappe.db.get_value(reference.reference_type, reference.reference_name, "outstanding_amount")
			frappe.db.set_value(reference.reference_type, reference.reference_name, \
				"outstanding_amount", flt(outstanding_amount) + flt(reference.paid_amount))
			frappe.get_doc(reference.reference_type, reference.reference_name).set_status(update=True)

	def get_rev_exp_accounting_journal(self, accounting_item):
		journal = frappe.db.get_value("Accounting Item", accounting_item, "accounting_journal")

		if journal:
			return journal
		else:
			frappe.throw(_("Please choose an accounting journal for accounting item {0}".format(accounting_item)))

	def get_bank_cash_accounting_journal(self):
		payment_type = frappe.db.get_value("Payment Method", self.payment_method, "payment_type")

		if payment_type == "Cash":
			accounting_item = frappe.db.get_value("Payment Method", self.payment_method, "accounting_item")
		else:
			bank_account = frappe.db.get_value("Payment Method", self.payment_method, "bank_account")
			accounting_item = frappe.db.get_value("Maia Bank Account", bank_account, "accounting_item")

		journal = frappe.db.get_value("Accounting Item", accounting_item, "accounting_journal")

		if journal and accounting_item:
			return accounting_item, journal
		else:
			frappe.throw(_("Please choose an accounting journal for accounting item {0}".format(accounting_item)))

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
		self.title = self.party or _("No party") + " - " + frappe.utils.fmt_money(self.paid_amount, currency=maia.get_default_currency())

	def post_gl_entries(self):
		self.make_references_gl_entries()
		self.make_pending_gl_entries()
		self.reverse_pending_gl_entries()
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
					"debit": abs(item.total_amount) if self.payment_type == "Outgoing payment" else 0,
					"credit": abs(item.total_amount) if self.payment_type == "Incoming payment" else 0,
					"currency": maia.get_default_currency(),
					"reference_type": doc.doctype,
					"reference_name": doc.name,
					"link_doctype": self.doctype,
					"link_docname": self.name,
					"accounting_journal": self.get_rev_exp_accounting_journal(item.accounting_item),
					"party": self.party,
					"practitioner": self.practitioner
				})
		else:
			entries.append({
				"posting_date": self.payment_date,
				"accounting_item": doc.accounting_item,
				"debit": abs(doc.amount) if self.payment_type == "Outgoing payment" else 0,
				"credit": abs(doc.amount) if self.payment_type == "Incoming payment" else 0,
				"currency": maia.get_default_currency(),
				"reference_type": doc.doctype,
				"reference_name": doc.name,
				"link_doctype": self.doctype,
				"link_docname": self.name,
				"accounting_journal": self.get_rev_exp_accounting_journal(doc.accounting_item),
				"party": self.party,
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
				"accounting_item": accounting_item.name,
				"debit": abs(self.pending_amount) if self.payment_type == "Outgoing payment" else 0,
				"credit": abs(self.pending_amount) if self.payment_type == "Incoming payment" else 0,
				"currency": maia.get_default_currency(),
				"reference_type": self.doctype,
				"reference_name": self.name,
				"link_doctype": self.doctype,
				"link_docname": self.name,
				"accounting_journal": self.get_rev_exp_accounting_journal(accounting_item.name),
				"party": self.party,
				"practitioner": self.practitioner
			})

			make_gl_entries(gl_entries)

	def reverse_pending_gl_entries(self):
		if self.previously_paid_amount and self.previously_paid_amount > 0:
			if not self.party:
				frappe.throw(_("Please select a party"))

			accounting_item = self.get_party_accounting_item()
			gl_entries = []

			gl_entries.append({
				"posting_date": self.payment_date,
				"accounting_item": accounting_item.name,
				"debit": abs(self.previously_paid_amount) if self.payment_type == "Incoming payment" else 0,
				"credit": abs(self.previously_paid_amount) if self.payment_type == "Outgoing payment" else 0,
				"currency": maia.get_default_currency(),
				"reference_type": self.doctype,
				"reference_name": self.name,
				"link_doctype": self.doctype,
				"link_docname": self.name,
				"accounting_journal": self.get_rev_exp_accounting_journal(accounting_item.name),
				"party": self.party,
				"practitioner": self.practitioner
			})

			make_gl_entries(gl_entries)

	def make_payment_gl_entries(self):
		gl_entries = []

		account, journal = self.get_bank_cash_accounting_journal()

		gl_entries.append({
			"posting_date": self.payment_date,
			"accounting_item": account,
			"debit": abs(self.paid_amount) if self.payment_type == "Incoming payment" else 0,
			"credit": abs(self.paid_amount) if self.payment_type == "Outgoing payment" else 0,
			"currency": maia.get_default_currency(),
			"reference_type": self.doctype,
			"reference_name": self.name,
			"link_doctype": self.doctype,
			"link_docname": self.name,
			"accounting_journal": journal,
			"party": self.party,
			"practitioner": self.practitioner
		})

		make_gl_entries(gl_entries)

	def set_outstanding_amount(self):
		for ref in self.get("payment_references"):
			outstanding = frappe.db.get_value(ref.reference_type, ref.reference_name, "outstanding_amount")
			frappe.db.set_value(ref.reference_type, ref.reference_name, "outstanding_amount", flt(outstanding) - flt(ref.paid_amount))
			frappe.get_doc(ref.reference_type, ref.reference_name).set_status(update=True)
			frappe.db.commit()

@frappe.whitelist()
def get_replaced_practitioner(date, practitioner):
	replacements = frappe.get_all("Replacement", \
			filters={"start_date": ["<=", date], "end_date": [">=", date], "substitute": practitioner}, \
			fields=["practitioner"])

	if replacements:
		return replacements[0]["practitioner"]

@frappe.whitelist()
def get_payment(dt, dn):
	source_doc = frappe.get_doc(dt, dn)

	payment = frappe.new_doc("Payment")
	payment.payment_type = "Incoming payment" if dt == "Revenue" else "Outgoing payment"
	payment.party_type = "Party" if source_doc.party else "Patient Record"
	payment.party = source_doc.party if source_doc.party else source_doc.patient
	payment.paid_amount = source_doc.outstanding_amount
	payment.payment_date = source_doc.transaction_date

	payment.append("payment_references", {
		'reference_type': dt,
		'reference_name': dn,
		'transaction_date': source_doc.transaction_date,
		'party': source_doc.party,
		'patient_record': source_doc.patient if dt=="Revenue" else None,
		'outstanding_amount': source_doc.outstanding_amount,
		'paid_amount': source_doc.outstanding_amount
	})

	return payment

@frappe.whitelist()
def get_list_payment(names, dt):
	names = json.loads(names)
	party_type = "Party"
	partys = frappe.get_all(dt, filters={"name": ["in", names]}, fields=["DISTINCT(party) as name"])
	if not partys or not partys[0]["name"]:
		party_type = "Patient Record"
		partys = frappe.get_all(dt, filters={"name": ["in", names]}, fields=["DISTINCT(patient) as name"])

	if len(partys) > 1:
		frappe.throw(_("Please select documents linked to the same party or patient"))
	elif partys[0]["name"]:
		payment = frappe.new_doc("Payment")
		payment.payment_type = "Incoming payment" if dt == "Revenue" else "Outgoing payment"
		payment.party_type = party_type
		payment.party = partys[0]["name"]
		payment.payment_date = nowdate()

		total_paid = 0
		for dn in names:
			fields = ["party", "transaction_date", "outstanding_amount"]
			if dt == "Revenue":
				fields.append("patient")
			source_doc = frappe.db.get_value(dt, dn, fields, as_dict=True)
			payment.append("payment_references", {
				'reference_type': dt,
				'reference_name': dn,
				'transaction_date': source_doc.transaction_date,
				'party': source_doc.party,
				'patient_record': source_doc.patient if dt=="Revenue" else None,
				'outstanding_amount': source_doc.outstanding_amount,
				'paid_amount': source_doc.outstanding_amount
			})
			total_paid += flt(source_doc.outstanding_amount)

		payment.paid_amount = total_paid
		return payment
	else:
		payment = frappe.new_doc("Payment")
		payment.payment_type = "Incoming payment" if dt == "Revenue" else "Outgoing payment"
		payment.payment_date = nowdate()

		return payment

@frappe.whitelist()
def get_outstanding_references(party_type, payment_type, party=None):
	dt = "Revenue" if payment_type == "Incoming payment" else "Expense"
	fields=["name", "amount", "outstanding_amount", "party", "transaction_date"]

	if dt == "Revenue":
		fields.append("patient")

	filters = {"outstanding_amount": [">", 0], "docstatus": 1}
	if party:
		party_filter = "party" if party_type == "Party" else "patient"
		filters[party_filter] = party

	references = frappe.get_all(dt, filters=filters, fields=fields)

	return [dict(r,**{"doctype": dt}) for r in references]

@frappe.whitelist()
def get_pending_amount(payment_type, party):
	filters = {"party": party}

	party_type = "Sales Party" if payment_type == "Incoming payment" else "Purchase Party"
	party_item = frappe.db.get_value("Accounting Item", dict(accounting_item_type=party_type), "name")
	filters["accounting_item"] = party_item

	result = frappe.get_all("General Ledger Entry", filters=filters, fields=["SUM(credit)-SUM(debit) as total"])

	if result and len(result) == 1:
		return flt(result[0]["total"]) if payment_type == "Incoming payment" else (0-flt(result[0]["total"]))

@frappe.whitelist()
def update_clearance_date(docname, date):
	current_clearance_date = frappe.db.get_value("Payment", docname, "clearance_date")

	frappe.db.set_value("Payment", docname, "clearance_date", getdate(date), update_modified=False)
	frappe.db.commit()

	payment = frappe.get_doc("Payment", docname)
	payment.set_status(update=True, status="Reconciled")

	if current_clearance_date:
		payment.add_comment('Comment', \
			_("Clearance date changed from {0} to {1}".format(formatdate(current_clearance_date), formatdate(date))))

@frappe.whitelist()
def update_clearance_dates(names, date):
	names = json.loads(names)
	print(names)
	for name in names:
		update_clearance_date(name, date)

def get_permission_query_conditions(user):
	return get_accounting_query_conditions("Payment", user)