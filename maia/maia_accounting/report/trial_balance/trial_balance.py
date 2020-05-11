# Copyright (c) 2020, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from maia.maia_accounting.report.maia_general_ledger.maia_general_ledger import get_opening_balance

def execute(filters=None):
	if not (filters.from_date and filters.to_date):
		frappe.throw(_("Please select a start and end date"))

	if not (filters.practitioner):
		frappe.throw(_("Please select a practitioner"))

	data = get_data(filters)
	columns = get_columns()

	return columns, data

def get_data(filters):
	accounting_items = sorted(frappe.get_all("Accounting Item", fields=["name", "accounting_number"]), key=lambda x:x.accounting_number)

	result = []

	for accounting_item in accounting_items:
		data_filters = { **filters, **{"accounting_item": accounting_item.name} }
		opening_balance = get_opening_balance(filters.from_date, data_filters)
		period_movements = get_period_movements(data_filters)
		closing_balance = get_closing_balance(opening_balance, period_movements)

		opening_amount = flt(opening_balance.get("debit", 0)) - flt(opening_balance.get("credit", 0))

		result.append({
			"accounting_item": (accounting_item.accounting_number or "") + " - " + accounting_item.name,
			"currency": "EUR",
			"opening_debit": abs(opening_amount) if opening_amount < 0 else 0,
			"opening_credit": opening_amount if opening_amount > 0 else 0,
			"debit": period_movements.get("debit", 0),
			"credit": period_movements.get("credit", 0),
			"closing_debit": closing_balance.get("debit", 0),
			"closing_credit": closing_balance.get("credit", 0)
		})

	output = [x for x in result if (x.get("opening_debit") or x.get("opening_debit") or x.get("debit") or x.get("credit") or x.get("closing_debit") or x.get("closing_credit"))]

	output.append({})
	output.append({
		"accounting_item": _("Total"),
		"currency": "EUR",
		"bold": 1,
		"opening_debit": sum([x.get("opening_debit", 0) for x in output]),
		"opening_credit": sum([x.get("opening_credit", 0) for x in output]),
		"debit": sum([x.get("debit", 0) for x in output]),
		"credit": sum([x.get("credit", 0) for x in output]),
		"closing_debit": sum([x.get("closing_debit", 0) for x in output]),
		"closing_credit": sum([x.get("closing_credit", 0) for x in output])
	})

	return output


def get_period_movements(filters):
	gl_filters = {
		"posting_date": ("between", (filters.get("from_date"), filters.get("to_date"))),
		"practitioner": filters.get("practitioner"),
		"accounting_item": filters.get("accounting_item"),
		"accounting_journal": ("!=", "Closing entries")
	}

	entries = frappe.get_all("General Ledger Entry", filters=gl_filters, fields=["SUM(credit) as credit, SUM(debit) as debit"])
	return {
		"debit": flt(entries[0].get("debit")) if entries else flt(0),
		"credit": flt(entries[0].get("credit")) if entries else flt(0)
	}

def get_closing_balance(opening, movements):
	amount = flt(opening.get("debit")) + flt(movements.get("debit")) - (flt(opening.get("credit")) + flt(movements.get("credit")))
	return {
		"debit": amount if amount > 0 else 0,
		"credit": abs(amount) if amount < 0 else 0
	}

def get_columns():
	return [
		{
			"fieldname": "accounting_item",
			"label": _("Accounting Item"),
			"fieldtype": "Link",
			"options": "Accounting Item",
			"width": 300
		},
		{
			"fieldname": "currency",
			"label": _("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"hidden": 1
		},
		{
			"fieldname": "opening_debit",
			"label": _("Opening (Dr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "opening_credit",
			"label": _("Opening (Cr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "debit",
			"label": _("Debit"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "credit",
			"label": _("Credit"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "closing_debit",
			"label": _("Closing (Dr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "closing_credit",
			"label": _("Closing (Cr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		}
	]