# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dokos and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
import os
from frappe import _
from frappe.utils import update_progress_bar
from maia.maia_accounting.doctype.payment.payment import get_payment

def execute():
	journal_entries = frappe.get_all("Journal Entry", dict(docstatus=1))
	second_round = []

	l = len(journal_entries)

	for i, entry in enumerate(journal_entries):
		journal_entry = frappe.get_doc("Journal Entry", entry.name)

		if journal_entry.title.endswith("Paiement de Frais de Repas"):
			make_meal_expense(journal_entry)

		elif journal_entry.title.endswith("Contributions Sociales"):
			make_social_contributions(journal_entry)

		elif journal_entry.voucher_type == "Depreciation Entry" or journal_entry.title.endswith("Frais de Repas"):
			continue

		else:
			second_round.append(journal_entry.name)

		with open(os.path.join(frappe.utils.get_bench_path(), "manual_migration.txt"), "wb") as migration_file:
			migration_file.write(bytes(",".join([str(i) for i in second_round]), 'utf-8'))

		update_progress_bar("Migrating Journal Entries", i, l)

	print(second_round)
	frappe.db.commit()

def make_meal_expense(journal_entry):
	for account in journal_entry.accounts:
		if account.reference_type:
			expense = make_meal_expense_doc(account.reference_type, account.reference_name)
			make_meal_payment(expense)

def make_meal_expense_doc(reference_type, reference_name):
	journal_entry = frappe.get_doc(reference_type, reference_name)

	expense = frappe.new_doc("Expense")
	expense.label = journal_entry.title
	expense.expense_type = "Meal expense"
	expense.amount = journal_entry.total_debit
	expense.practitioner = frappe.db.get_value("Professional Information Card", dict(company=journal_entry.company), "name")
	expense.transaction_date = journal_entry.posting_date
	expense.with_items = 1
	expense.note = journal_entry.user_remark

	account_map = get_account_map()

	for account in journal_entry.accounts:
		if not account.party:
			expense_item = {
				"label": account.account,
				"total_amount": flt(account.debit_in_account_currency) if flt(account.debit_in_account_currency) > 0 else -flt(account.credit_in_account_currency),
				"accounting_item": account_map[account.account[:-5]]
			}

			expense.append("expense_items", expense_item)
		else:
			expense.party = make_new_party(account.party)

	expense.insert(ignore_permissions=True)
	expense.submit()

	return expense

def make_meal_payment(expense):
	payment = get_payment(expense.doctype, expense.name)
	payment.practitioner = expense.practitioner
	payment.payment_method = frappe.db.get_value("Payment Method", dict(default_outgoing=1), "name")
	payment.insert(ignore_permissions=True)
	payment.submit()

def make_social_contributions(journal_entry):
	for account in journal_entry.accounts:
		if account.reference_type:
			expense = make_social_contributions_doc(account.reference_type, account.reference_name)
			make_social_contributions_payment(expense)

def make_social_contributions_doc(reference_type, reference_name):
	journal_entry = frappe.get_doc(reference_type, reference_name)

	expense = frappe.new_doc("Expense")
	expense.label = journal_entry.title
	expense.expense_type = "Social contributions"
	expense.amount = journal_entry.total_debit
	expense.practitioner = frappe.db.get_value("Professional Information Card", dict(company=journal_entry.company), "name")
	expense.transaction_date = journal_entry.posting_date
	expense.with_items = 1
	expense.note = journal_entry.user_remark

	account_map = get_account_map()

	for account in journal_entry.accounts:
		if not account.party:
			expense_item = {
				"label": account.account,
				"total_amount": flt(account.debit_in_account_currency) if flt(account.debit_in_account_currency) > 0 else -flt(account.credit_in_account_currency),
				"accounting_item": account_map[account.account[:-5]]
			}

			expense.append("expense_items", expense_item)
		else:
			expense.party = make_new_party(account.party)

	expense.insert(ignore_permissions=True)
	expense.submit()

	return expense

def make_social_contributions_payment(expense):
	payment = get_payment(expense.doctype, expense.name)
	payment.practitioner = expense.practitioner
	payment.payment_method = frappe.db.get_value("Payment Method", dict(default_outgoing=1), "name")
	payment.insert(ignore_permissions=True)
	payment.submit()

def make_new_party(name):
	if not frappe.db.exists("Party", name):
		party = frappe.new_doc("Party")
		party.party_name = name
		party.is_supplier = 1
		party.insert(ignore_permissions=True)
		return party.name

	else:
		return name

def make_personal_debit_payment(journal_entry):
	new_payment = frappe.new_doc("Payment")
	new_payment.payment_date = journal_entry.posting_date
	new_payment.practitioner = expense.practitioner
	new_payment.payment_type = "Outgoing payment"
	new_payment.payment_method = pi.mode_of_payment if pi.mode_of_payment else frappe.db.get_value("Payment Method", dict(default_incoming=1), "name")
	new_payment.party_type = "Party"
	new_payment.party = pi.supplier
	new_payment.paid_amount = flt(pi.paid_amount)
	new_payment.append("payment_references", {
		"reference_type": "Expense",
		"reference_name": expense.name,
		"paid_amount": flt(pi.paid_amount)
	})
	new_payment.clearance_date = pi.clearance_date

	new_payment.insert(ignore_permissions=True)
	new_payment.submit()

def get_account_map():
	return {
		"6378 - CSG Déductible": "CSG déductible",
		"512100  - BNP PARIBAS": "BNP PARIBAS",
		"645 - Charges de sécurité sociale et de prévoyance": "Charges sociales URSSAF",
		"431 - Sécurité sociale": "Fournisseurs",
		"108900 - Compte de l'exploitant": "Personnel - Exploitant",
		"4011 - Fournisseurs - Achats de biens ou de prestations de services": "Fournisseurs",
		"646 - Cotisations sociales personnelles de l'exploitant":  "Charges sociales URSSAF",
		"58 - Virements internes": "Virement Interne",
		"5311 - Caisse en monnaie nationale": _("Cash"),
		"625700 - Frais de repas déductibles": "Autres frais de déplacements",
		"2183 - Matériel de bureau et matériel informatique": "Fournitures de bureau",
		"68112 - Immobilisations corporelles": "Dotations aux amortissements",
		"2155 - Outillage": "Petit outillage",
		"2184 - Mobilier": "Location matériel et mobilier",
		"791 - Transferts de charges d'exploitation": "Gains divers",
		"443010 - Organismes de formations agréé": "Fournisseurs",
		"410 - Clients et Comptes rattachés": "Clients",
		"654  - Pertes sur créances irrécouvrables": "Pertes diverses"
	}