# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
import os
from frappe import _
from frappe.utils import update_progress_bar
import json

def execute():
	reload_docs_for_migration()

	make_cpam_urssaf_parties()
	create_new_coa()
	allocate_accounting_items_to_codifications()
	bank_map = create_bank_accounts()
	migrate_payment_methods(bank_map)
	add_fiscal_years()
	frappe.db.commit()

	sales_invoices = frappe.get_all("Sales Invoice", dict(docstatus=1), limit=None)
	to_be_credited = []

	l = len(sales_invoices)
	print(l)


	for i, invoice in enumerate(sales_invoices):
		si = frappe.get_doc("Sales Invoice", invoice.name)
		if si.return_against:
			if frappe.db.exists("Revenue", dict(label=si.return_against)):
				initial_revenue = frappe.get_doc("Revenue", dict(label=si.return_against))
				linked_payments = frappe.get_all("Payment References", filters={"reference_type": "Revenue", "reference_name": initial_revenue.name}, fields=["parent"])
				for p in linked_payments:
					frappe.get_doc("Payment", p.parent).cancel()					
				initial_revenue.cancel()
			else:
				to_be_credited.append(si.return_against)

		revenue = frappe.new_doc("Revenue")
		revenue.label = si.name
		revenue.patient = si.patient_record
		if si.patient_record != si.customer:
			revenue.revenue_type = "Social Security"
			revenue.party = make_new_party(si.customer)
		revenue.practitioner = frappe.db.get_value("Professional Information Card", dict(company=si.company), "name")
		revenue.transaction_date = si.posting_date
		revenue.amount = si.grand_total
		revenue.codifications = []
		revenue.note = ""

		if si.consultation_reference:
			revenue.consultation_type = get_reference_doctype(si)
			if revenue.consultation_type:
				revenue.consultation = si.consultation_reference

		for item in si.items:
			revenue_item = {
				"codification": item.item_code,
				"accounting_item": frappe.db.get_value("Codification", item.item_code, "accounting_item"),
				"qty": item.qty,
				"unit_price": item.rate
			}

			if frappe.db.exists("Codification", item.item_code):
				revenue.with_items = 1
				revenue.append("codifications", revenue_item)
			else:
				revenue.accounting_item = frappe.db.get_value("Accounting Item", dict(accounting_journal="Sales"), "name")
				revenue.with_items = 0
				revenue.note += json.dumps({
					"codification": item.item_code,
					"accounting_item": frappe.db.get_value("Codification", item.item_code, "accounting_item"),
					"qty": item.qty,
					"unit_price": item.rate
				})

		revenue.insert(ignore_permissions=True, ignore_links=True)
		revenue.submit()
		frappe.db.commit()

		if si.name in to_be_credited:
			revenue.cancel()
			to_be_credited.remove(si.name)

		if si.outstanding_amount == si.grand_total and si.grand_total != 0:
			pass
		elif revenue.docstatus == 1:
			create_payment(si, revenue)

		update_progress_bar("Migrating Sales Invoices", i, l)

	frappe.db.commit()

def make_cpam_urssaf_parties():
	if not frappe.db.exists("Party", "CPAM"):
		party = frappe.new_doc("Party")
		party.party_name = "CPAM"
		party.is_customer = 1
		party.insert(ignore_permissions=True)

	if not frappe.db.exists("Party", "URSSAF"):
		party = frappe.new_doc("Party")
		party.party_name = "URSSAF"
		party.is_social_contribution = 1
		party.insert(ignore_permissions=True)

def create_new_coa():
	path = os.path.join(frappe.get_module_path('maia_accounting'), "doctype", "accounting_item", "plan_comptable.json")
	pc = frappe.get_file_json(path)
	for p in pc:
		if not frappe.db.exists("Accounting Item", p):
			doc = frappe.new_doc("Accounting Item")
			doc.accounting_item = p
			doc.update(pc[p])
			doc.insert(ignore_permissions=True)

def allocate_accounting_items_to_codifications():
	codifications = frappe.get_all("Codification", filters={"accounting_item": ""})

	for codification in codifications:
		frappe.db.set_value("Codification", codification.name, "accounting_item", "Recettes encaissées, Honoraire")

def migrate_payment_methods(bank_map):
	mode_of_payments_accounts = frappe.get_all("Mode of Payment Account", fields=["parent", "company"])

	for mopa in mode_of_payments_accounts:
		mop = frappe.get_doc("Mode of Payment", mopa.parent)
		practitioner = frappe.db.get_value("Professional Information Card", dict(company=mopa.company), "name")
		if not frappe.db.exists("Payment Method", mop.name):
			pm = frappe.new_doc("Payment Method")
			pm.payment_method = mop.name
			pm.payment_type = mop.type
			if mop.type == "Cash":
				pm.accounting_item = make_cash_accounting_item()
			else:
				pm.bank_account = bank_map[practitioner]
			pm.insert(ignore_permissions=True)

	used_pay_mop = frappe.db.sql("""select mode_of_payment, count(name) from `tabPayment Entry` where payment_type="Pay" group by mode_of_payment order by count(name) DESC""")
	used_rec_mop = frappe.db.sql("""select mode_of_payment, count(name) from `tabPayment Entry` where payment_type="Receive" group by mode_of_payment order by count(name) DESC""")

	for mp in frappe.get_all("Mode of Payment", fields=["name", "type"]):
		if mp.name not in [x["name"] for x in frappe.get_all("Payment Method")]:
			pm = frappe.new_doc("Payment Method")
			pm.payment_method = mp.name
			pm.payment_type = mp.type
			if mp.type == "Cash":
				pm.accounting_item = make_cash_accounting_item()
			else:
				pm.bank_account = bank_map[practitioner]
			pm.insert(ignore_permissions=True)

	if used_pay_mop and used_pay_mop[0][0]:
			frappe.set_value("Payment Method", used_pay_mop[0][0], "default_outgoing", 1)

	if used_rec_mop and used_rec_mop[0][0]:
		frappe.set_value("Payment Method", used_rec_mop[0][0], "default_incoming", 1)

def create_bank_accounts():
	accounts_list = []
	for item in frappe.get_all("Mode of Payment Account", fields=["default_account", "company"]):
		if item not in accounts_list:
			accounts_list.append(item)

	bank_map = {}
	number = 0
	for line in accounts_list:
		if not line.default_account:
			continue

		practitioner = frappe.db.get_value("Professional Information Card", dict(company=line.company), "name")
		abbr = frappe.db.get_value("Company", line.company, "abbr")
		bank_name = line.default_account.split('-')[1].strip()

		if not frappe.db.exists("Maia Bank Account", bank_name):
			bank = frappe.new_doc("Maia Bank Account")
			bank.bank_account_name = bank_name
			number += 1
			bank.accounting_item = add_bank_accounting_item(bank_name, number)
			bank.insert(ignore_permissions=True)

			bank_map.update({practitioner: bank.name})

		else:
			bank_map.update({practitioner: bank_name})

	return bank_map

def add_bank_accounting_item(name, number):
	if not frappe.db.exists("Accounting Item", name):
		accounting_item = frappe.new_doc("Accounting Item")
		accounting_item.accounting_item = name
		accounting_item.accounting_item_type = "Bank"
		accounting_item.accounting_journal = "Bank"
		accounting_item.accounting_number = (512000 + number * 10)
		accounting_item.insert(ignore_permissions=True)
		frappe.db.commit()
		return accounting_item.name
	else:
		return name

def make_cash_accounting_item():
	if not frappe.db.exists("Accounting Item", dict(accounting_item_type="Cash")):
		accounting_item = frappe.new_doc("Accounting Item")
		accounting_item.accounting_item = _("Cash")
		accounting_item.accounting_item_type = "Cash"
		accounting_item.accounting_journal = "Cash"
		accounting_item.accounting_number = 531000
		accounting_item.insert(ignore_permissions=True)
		frappe.db.commit()
		return accounting_item.name
	else:
		return frappe.db.get_value("Accounting Item", dict(accounting_item_type="Cash"), "name")

def make_new_party(name):
	if not frappe.db.exists("Party", name):
		party = frappe.new_doc("Party")
		party.party_name = name
		party.is_customer = 1 if name != "CPAM" else 0
		party.is_social_security = 0 if name != "CPAM" else 1
		party.insert(ignore_permissions=True)
		return party.name

	else:
		return name

def get_reference_doctype(si):
	if si.consultation_reference.startswith("PGC"):
		return "Pregnancy Consultation"
	elif si.consultation_reference.startswith("BPC"):
		return "Birth Preparation Consultation"
	elif si.consultation_reference.startswith("EPC"):
		return "Early Postnatal Consultation"
	elif si.consultation_reference.startswith("PRC"):
		return "Perineum Rehabilitation Consultation"
	elif si.consultation_reference.startswith("PNC"):
		return "Postnatal Consultation"
	elif si.consultation_reference.startswith("GC"):
		return "Gynecological Consultation"
	elif si.consultation_reference.startswith("PIC"):
		return "Prenatal Interview Consultation"
	elif si.consultation_reference.startswith("FC"):
		return "Free Consultation"
	else:
		return None

def create_payment(si, revenue):
	if si.is_pos:
		for line in si.payments:
			new_payment = frappe.new_doc("Payment")
			new_payment.payment_date = si.posting_date
			new_payment.payment_type = "Incoming payment"
			new_payment.practitioner = revenue.practitioner
			new_payment.payment_method = line.mode_of_payment if line.mode_of_payment else frappe.db.get_value("Payment Method", dict(default_incoming=1), "name")
			new_payment.party_type = "Patient Record"
			new_payment.party = si.customer
			new_payment.paid_amount = flt(line.amount)
			new_payment.append("payment_references", {
				"reference_type": "Revenue",
				"reference_name": revenue.name,
				"paid_amount": flt(line.amount)
			})
			new_payment.clearance_date = line.clearance_date

			new_payment.insert(ignore_permissions=True, ignore_links=True)
			new_payment.submit()
	else:
		references = frappe.get_all("Payment Entry Reference", filters={"docstatus": 1, "reference_doctype": "Sales Invoice", "reference_name": si.name}, \
			fields=["parent", "allocated_amount"])

		total = 0
		payment_references = []
		for reference in references:
			payment = frappe.get_doc("Payment Entry", reference.parent)

			total += flt(reference.allocated_amount)

			if len(payment_references) > 0:
				payment_references[0]["paid_amount"] += flt(reference.allocated_amount)
			else:
				payment_references.append({
					"reference_type": "Revenue",
					"reference_name": revenue.name,
					"paid_amount": flt(reference.allocated_amount)
				})

		if references and total > 0:
			new_payment = frappe.new_doc("Payment")
			new_payment.payment_date = payment.posting_date
			new_payment.payment_type = "Incoming payment"
			new_payment.practitioner = revenue.practitioner
			new_payment.payment_method = payment.mode_of_payment if payment.mode_of_payment else frappe.db.get_value("Payment Method", dict(default_incoming=1), "name")
			new_payment.party_type = "Patient Record" if payment.party != "CPAM" else "Party"
			new_payment.party = payment.party
			new_payment.patient = revenue.patient
			new_payment.paid_amount = total
			new_payment.clearance_date = payment.clearance_date
			new_payment.payment_references = []

			for ref in payment_references:
				new_payment.append("payment_references", ref)

			new_payment.insert(ignore_permissions=True, ignore_links=True)
			new_payment.submit()

def reload_docs_for_migration():
	frappe.reload_doc('maia_accounting', 'doctype', 'party')
	frappe.reload_doc('maia_accounting', 'doctype', 'payment')
	frappe.reload_doc('maia_accounting', 'doctype', 'payment_references')
	frappe.reload_doc('maia_accounting', 'doctype', 'expense')
	frappe.reload_doc('maia_accounting', 'doctype', 'expense_items')
	frappe.reload_doc('maia_accounting', 'doctype', 'revenue')
	frappe.reload_doc('maia_accounting', 'doctype', 'revenue_items')
	frappe.reload_doc('maia_accounting', 'doctype', 'accounting_item')
	frappe.reload_doc('maia_accounting', 'doctype', 'general_ledger_entry')
	frappe.reload_doc('maia_accounting', 'doctype', 'maia_asset')
	frappe.reload_doc('maia_accounting', 'doctype', 'maia_asset_depreciation')
	frappe.reload_doc('maia_accounting', 'doctype', 'maia_bank_account')
	frappe.reload_doc('maia_accounting', 'doctype', 'maia_fiscal_year')
	frappe.reload_doc('maia_accounting', 'doctype', 'miscellaneous_operation')
	frappe.reload_doc('maia_accounting', 'doctype', 'miscellaneous_operation_items')
	frappe.reload_doc('maia_accounting', 'doctype', 'payment_method')
	frappe.reload_doc('maia_accounting', 'doctype', 'meal_expense_deduction')

	frappe.reload_doc('maia', 'doctype', 'codification')

def add_fiscal_years():
	fiscal_years = [
		{"year": 2016, "start": "2016-01-01", "end": "2016-12-31"},
		{"year": 2017, "start": "2017-01-01", "end": "2017-12-31"},
		{"year": 2018, "start": "2018-01-01", "end": "2018-12-31"},
		{"year": 2019, "start": "2019-01-01", "end": "2019-12-31"},
	]

	for fy in fiscal_years:
		try:
			frappe.get_doc({
				"doctype": "Maia Fiscal Year",
				"year": fy["year"],
				"year_start_date": fy["start"],
				"year_end_date": fy["end"]
			}).insert(ignore_permissions=True)
		except Exception as e:
			print(e)