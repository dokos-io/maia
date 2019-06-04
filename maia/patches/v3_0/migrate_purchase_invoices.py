# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
import os
from frappe import _
from frappe.utils import update_progress_bar

def execute():

	add_meal_deductions()

	purchase_invoices = frappe.get_all("Purchase Invoice", dict(docstatus=1), limit=None)
	to_be_debited = []
	account_map = get_account_map()

	l = len(purchase_invoices)

	for i, invoice in enumerate(purchase_invoices):
		pi = frappe.get_doc("Purchase Invoice", invoice.name)
		if pi.return_against:
			if frappe.db.exists("Expense", dict(label=pi.return_against)):
				initial_expense = frappe.get_doc("Expense", dict(label=pi.return_against))
				linked_payments = frappe.get_all("Payment References", filters={"reference_type": "Expense", "reference_name": initial_expense.name}, fields=["parent"])
				for p in linked_payments:
					frappe.get_doc("Payment", p.parent).cancel()
				initial_expense.cancel()
			else:
				to_be_debited.append(pi.return_against)

		expense = frappe.new_doc("Expense")
		expense.label = pi.name
		expense.party = make_new_party(pi.supplier)
		expense.practitioner = frappe.db.get_value("Professional Information Card", dict(company=pi.company), "name")
		expense.transaction_date = pi.posting_date
		expense.with_items = 1
		expense.amount = pi.grand_total
		expense.expense_items = []

		for item in pi.items:
			if item.asset:
				item_group = "Achat d'immobilisations"
			else:
				item_group = frappe.db.get_value("Item", item.item_code, "item_group")
			expense_item = {
				"label": item.item_code,
				"accounting_item": account_map[item_group],
				"qty": item.qty,
				"total_amount": item.amount
			}

			expense.append("expense_items", expense_item)

		expense.insert(ignore_permissions=True)
		expense.submit()

		if pi.name in to_be_debited:
			expense.cancel()
			to_be_debited.remove(pi.name)

		if pi.outstanding_amount == pi.grand_total and pi.grand_total != 0:
			pass
		elif expense.docstatus == 1:
			create_payment(pi, expense)

		update_progress_bar("Migrating Purchase Invoices", i, l)

	frappe.db.commit()

def make_new_party(name):
	if not frappe.db.exists("Party", name):
		party = frappe.new_doc("Party")
		party.party_name = name
		party.is_supplier = 1
		party.insert(ignore_permissions=True)
		return party.name

	else:
		return name

def create_payment(pi, expense):
	if pi.is_paid:
		new_payment = frappe.new_doc("Payment")
		new_payment.payment_date = pi.posting_date
		new_payment.payment_type = "Outgoing payment"
		new_payment.practitioner = expense.practitioner
		new_payment.payment_method = pi.mode_of_payment if pi.mode_of_payment else frappe.db.get_value("Payment Method", dict(default_outgoing=1), "name")
		new_payment.party_type = "Party"
		new_payment.party = pi.supplier
		new_payment.paid_amount = flt(pi.paid_amount)
		new_payment.append("payment_references", {
			"reference_type": "Expense",
			"reference_name": expense.name,
			"paid_amount": flt(pi.paid_amount)
		})

		new_payment.insert(ignore_permissions=True)
		new_payment.submit()

	else:
		references = frappe.get_all("Payment Entry Reference", filters={"docstatus": 1, "reference_doctype": "Purchase Invoice", "reference_name": pi.name}, \
			fields=["parent", "allocated_amount"])

		total = 0
		payment_references = []
		for reference in references:
			payment = frappe.get_doc("Payment Entry", reference.parent)

			total += flt(reference.allocated_amount)

			payment_references.append({
				"reference_type": "Expense",
				"reference_name": expense.name,
				"paid_amount": flt(reference.allocated_amount)
			})

		if references and total > 0:
			new_payment = frappe.new_doc("Payment")
			new_payment.payment_date = payment.posting_date
			new_payment.payment_type = "Outgoing payment"
			new_payment.practitioner = expense.practitioner
			new_payment.payment_method = payment.mode_of_payment if payment.mode_of_payment else frappe.db.get_value("Payment Method", dict(default_outgoing=1), "name")
			new_payment.party_type = "Party"
			new_payment.party = payment.party
			new_payment.paid_amount = total
			new_payment.clearance_date = payment.clearance_date
			new_payment.payment_references = []

			for ref in payment_references:
				new_payment.append("payment_references", ref)

			new_payment.insert(ignore_permissions=True)
			new_payment.submit()


def get_account_map():
	return {
		"Frais de Véhicules": "Frais de véhicule",
		"Autres Frais de Déplacement": "Autres frais de déplacements",
		"Frais Financiers": "Agios, frais de banque",
		"Autres Frais Divers de Gestion": "Autres frais divers de gestion",
		"Cotisations Syndicales et Professionnelles": "Cotisations syndicales et professionnelles",
		"Actes et Contentieux": "Frais d'actes et contentieux",
		"Fournitures de Bureau, Documentation, PTT": "Fournitures de bureau",
		"Frais de Réceptions, de Représentations, de Congrès": "Frais de réception, congrès...",
		"Charges Sociales Personnelles": "Charges sociales URSSAF",
		"Primes d'Assurance": "Assurances, hors véhicule",
		"Honoraires ne constituant pas de Rétrocession": "Honoraires non rétrocédés",
		"Chauffage, Eau, Gaz, Electricité": "Chauffage,eau,gaz,électricité",
		"Petit Outillage": "Petit outillage",
		"Personnel Intérimaire": "Personnel intérimaire",
		"Entretien et Réparations": "Entretien et réparations",
		"Location de Matériel et de Mobilier": "Location matériel et mobilier",
		"Loyer et Charges Locatives": "Loyers et charges locatives",
		"Achats": "Achats",
		"Achat d'immobilisations": "Achat d'immobilisations"
	}

def add_meal_deductions():
	deductions = [
		{"fiscal_year": 2016, "deductible_amount": 4.70, "limit": 18.3},
		{"fiscal_year": 2017, "deductible_amount": 4.75, "limit": 18.4},
		{"fiscal_year": 2018, "deductible_amount": 4.80, "limit": 18.6},
		{"fiscal_year": 2019, "deductible_amount": 4.75, "limit": 18.8}
	]

	for d in deductions:
		doc = frappe.get_doc({
			"doctype": "Meal Expense Deduction",
			"fiscal_year": d["fiscal_year"],
			"deductible_amount": d["deductible_amount"],
			"limit": d["limit"]
		})
		doc.insert()
		doc.submit()