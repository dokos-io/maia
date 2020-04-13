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
	print(data)
	return columns, data

def get_data(filters):
	accounting_items = frappe.get_all("Accounting Item")

	output = []

	for accounting_item in accounting_items:
		data_filters = { **filters, **{"accounting_item": accounting_item.name} }
		opening_balance = get_opening_balance(filters.from_date, data_filters)
		period_movements = get_period_movements(data_filters)
		closing_balance = get_closing_balance(opening_balance, period_movements)

		output.append({
			"accounting_item": accounting_item.name,
			"currency": "EUR",
			"opening_debit": flt(opening_balance.get("debit", 0)),
			"opening_credit":  flt(opening_balance.get("credit", 0)),
			"debit": period_movements.get("debit", 0),
			"credit": period_movements.get("credit", 0),
			"closing_debit": closing_balance.get("debit", 0),
			"closing_credit": closing_balance.get("credit", 0)
		})

	return output


def get_period_movements(filters):
	gl_filters = {
		"posting_date": ("between", (filters.get("from_date"), filters.get("to_date"))),
		"practitioner": filters.get("practitioner"),
		"accounting_item": filters.get("accounting_item")
	}

	entries = frappe.get_all("General Ledger Entry", filters=gl_filters, fields=["SUM(credit) as credit, SUM(debit) as debit"])
	return {
		"debit": flt(entries[0].get("debit")) if entries else flt(0),
		"credit": flt(entries[0].get("credit")) if entries else flt(0)
	}

def get_closing_balance(opening, movements):
	return {
		"debit": flt(opening.get("debit")) + flt(movements.get("debit")),
		"credit": flt(opening.get("credit")) + flt(movements.get("credit"))
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