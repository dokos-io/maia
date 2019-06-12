# Copyright (c) 2013, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, flt, formatdate
from dateutil.relativedelta import relativedelta
from collections import namedtuple

from maia.maia_accounting.utils import get_balance_on

def execute(filters=None):
	# Bank accounts
	bank_accounts = frappe.get_all("Maia Bank Account", fields=["name", "accounting_item"])

	# Cash account
	cash_account = namedtuple('CashAccount', 'name, accounting_item,account_type')
	cash_account.name = frappe.db.get_value("Accounting Item", dict(accounting_item_type="Cash"), "name")
	cash_account.accounting_item = frappe.db.get_value("Accounting Item", dict(accounting_item_type="Cash"), "accounting_item")

	columns = get_columns(filters, bank_accounts, cash_account)
	data = get_data(filters, bank_accounts, cash_account)

	return columns, data

def get_data(filters, bank_accounts, cash_account):
	data = init_data(filters)

	for bank_account in bank_accounts:
		gl_entries = get_gl_entries(filters, bank_account)

		balances = calculate_balances(filters, gl_entries, data)
		data = add_balances_to_data(filters, bank_account, data, balances)

	gl_entries = get_gl_entries(filters, cash_account)
	balances = calculate_balances(filters, gl_entries, data)
	data = add_balances_to_data(filters, cash_account, data, balances)

	return data

def get_gl_entries(filters, bank_account):
	gl_entries = frappe.db.sql(
		"""
		select
		gl.posting_date, gl.accounting_item, gl.debit, gl.credit,
		gl.link_docname, pay.clearance_date, pay.party
		from `tabGeneral Ledger Entry` gl
		left join `tabPayment` pay on gl.link_doctype='Payment' and gl.link_docname=pay.name
		where gl.practitioner=%(practitioner)s
		and gl.accounting_item='{accounting_item}'
		{conditions}
		order by posting_date, accounting_item
		""".format(
			accounting_item=bank_account.accounting_item,
			conditions=get_conditions(filters)
		), filters, as_dict=1)

	return gl_entries

def calculate_balances(filters, gl_entries, data):
	balances = {
		"uncredited y-1": {"value": 0, "entries": [], "line": 2, "index": [data.index(x) for x in data if x["line"] == 2][0]},
		"undebited y-1": {"value": 0, "entries": [], "line": 3, "index": [data.index(x) for x in data if x["line"] == 3][0]},
		"uncredited y": {"value": 0, "entries": [], "line": 7, "index": [data.index(x) for x in data if x["line"] == 7][0]},
		"undebited y": {"value": 0, "entries": [], "line": 8, "index": [data.index(x) for x in data if x["line"] == 8][0]},
		"revenue": {"value": 0, "line": 11},
		"expense": {"value": 0, "line": 12}
	}

	def update_value_in_dict(data, key, acc_type, gle):
		value = flt(gle.credit) if acc_type == "credit" else flt(gle.debit)
		data[key]["value"] += value
		if "entries" in data[key] and value > 0:
			data[key]["entries"].append(gle)

	from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
	for gle in gl_entries:
		if gle.posting_date>=from_date and gle.posting_date<=to_date and (not gle.clearance_date or gle.clearance_date > to_date):
			update_value_in_dict(balances, 'uncredited y', 'debit', gle)
			update_value_in_dict(balances, 'undebited y', 'credit', gle)

		elif gle.clearance_date and gle.clearance_date >= from_date and gle.posting_date < from_date:
			update_value_in_dict(balances, 'uncredited y-1', 'debit', gle)
			update_value_in_dict(balances, 'undebited y-1', 'credit', gle)

		if gle.posting_date>=from_date and gle.posting_date<=to_date:
			update_value_in_dict(balances, 'revenue', 'debit', gle)
			update_value_in_dict(balances, 'expense', 'credit', gle)

	return balances

def get_conditions(filters):
	conditions = []

	from frappe.desk.reportview import build_match_conditions
	match_conditions = build_match_conditions("General Ledger Entry")

	if match_conditions:
		conditions.append(match_conditions)

	return "and {}".format(" and ".join(conditions)) if conditions else ""

def add_balances_to_data(filters, bank_account, data, balances):
	bank_account_field = bank_account.name.lower().replace(" ", "_")

	bank_balance = get_bank_balance(filters.get("from_date"), filters.get("to_date"), bank_account.name)

	if (bank_balance["start"] is None or bank_balance["end"] is None) and isinstance(bank_account, dict):
		frappe.msgprint(_("Please add the initial and final bank statement values for {0} through the action button").format(bank_account.name))

	calculated_balance = get_balance_on(account=bank_account.accounting_item, date=filters.get("from_date"), practitioner=filters.get("practitioner")) or 0
	start_bank_balance = bank_balance["start"] or 0
	end_bank_balance = bank_balance["end"] or 0

	for d in data:
		if d["line"] == 0:
			d[bank_account_field] = start_bank_balance
		elif d["line"] == 5:
			d[bank_account_field] = end_bank_balance
		elif d["line"] == 1:
			d[bank_account_field] = balances["uncredited y-1"]["value"]
		elif d["line"] == 2:
			d[bank_account_field] = balances["undebited y-1"]["value"]
		elif d["line"] == 3:
			d[bank_account_field] = start_bank_balance + balances["uncredited y-1"]["value"] - balances["undebited y-1"]["value"]
		elif d["line"] == 6:
			d[bank_account_field] = balances["uncredited y"]["value"]
		elif d["line"] == 7:
			d[bank_account_field] = balances["undebited y"]["value"]
		elif d["line"] == 8:
			d[bank_account_field] = end_bank_balance + balances["uncredited y"]["value"] - balances["undebited y"]["value"]
		elif d["line"] == 10:
			d[bank_account_field] = calculated_balance
		elif d["line"] == 11:
			d[bank_account_field] = balances["revenue"]["value"]
		elif d["line"] == 12:
			d[bank_account_field] = balances["expense"]["value"]
		elif d["line"] == 13:
			d[bank_account_field] = calculated_balance + balances["revenue"]["value"] - balances["expense"]["value"]

	data = add_entries_to_data(bank_account_field, data, balances)

	return data

@frappe.whitelist()
def get_bank_balance(from_date, to_date, bank_account):
	return {
		"start": frappe.db.get_value("Bank Statement Balance", dict(date=getdate(from_date), bank_account=bank_account), "balance"),
		"end": frappe.db.get_value("Bank Statement Balance", dict(date=getdate(to_date), bank_account=bank_account), "balance")
	}

def add_entries_to_data(bank_account_field, data, balances):
	lines = ["undebited y", "uncredited y", "undebited y-1", "uncredited y-1"]
	for line in lines:
		entries = []
		for entry in balances[line]["entries"]:
			entries.append({
				"description": entry.party + " : " + entry.link_docname if entry.party else entry.link_docname,
				bank_account_field: flt(entry.credit) if flt(entry.credit) > 0 else flt(entry.debit),
				"indent": 1,
				"line": 999
			})

		i = balances[line]["index"]
		for e in entries:
			data.insert(i, e)
			i += 1

	return data


def init_data(filters):
	previous_year = (getdate(filters.get("from_date")) - relativedelta(years=1)).year
	current_year = getdate(filters.get("to_date")).year
	from_date = formatdate(filters.get("from_date"))
	to_date = formatdate(filters.get("to_date"))


	return [
		{"line": 0, "description": _("Bank statement balance on {0}").format(from_date), "indent": 0},
		{"line": 1, "description": _("Revenue from {0} uncredited before the {1}").format(previous_year, from_date), "indent": 0},
		{"line": 2, "description": _("Expense from {0} undebited before the {1}").format(previous_year, from_date), "indent": 0},
		{"line": 3, "description": _("Calculated accounting balance on {0}").format(from_date), "indent": 0},
		{"line": 4},
		{"line": 5, "description": _("Bank statement balance on {0}").format(to_date), "indent": 0, "index": 5},
		{"line": 6, "description": _("Revenue from {0} uncredited before the {1}").format(current_year, to_date), "indent": 0},
		{"line": 7, "description": _("Expense from {0} undebited before the {1}").format(current_year, to_date), "indent": 0},
		{"line": 8, "description": _("Calculated accounting balance on {0}").format(to_date), "indent": 0},
		{"line": 9},
		{"line": 10, "description": _("Accounting balance on {0}").format(from_date), "indent": 0},
		{"line": 11, "description": _("Revenue from {0}").format(current_year), "indent": 0},
		{"line": 12, "description": _("Expense from {0}").format(current_year), "indent": 0},
		{"line": 13, "description": _("Accounting balance on {0}").format(to_date), "indent": 0}
	]


def get_columns(filters, bank_accounts, cash_account):
	columns = [
		{
			"fieldname": "description",
			"fieldtype": "Data",
			"width": 400
		}
	]

	for bank_account in bank_accounts:
		columns.extend([
			{
				"label": bank_account.name,
				"fieldname": bank_account.name.lower().replace(" ", "_"),
				"fieldtype": "Currency",
				"width": 150
			}
		])

	columns.extend([
		{
			"label": cash_account.name,
			"fieldname": cash_account.name.lower().replace(" ", "_"),
			"fieldtype": "Currency",
			"width": 150
		}
	])

	return columns