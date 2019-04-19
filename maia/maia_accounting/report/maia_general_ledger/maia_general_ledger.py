# Copyright (c) 2019, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, cstr, flt, fmt_money
from frappe import _, _dict

def execute(filters=None):
	if not filters:
		return [], []

	account_details = {}

	for acc in frappe.db.sql("""select name from `tabAccounting Item`""", as_dict=1):
		account_details.setdefault(acc.name, acc)

	validate_filters(filters, account_details)

	columns = get_columns(filters)

	res = get_result(filters, account_details)

	return columns, res


def validate_filters(filters, account_details):
	if filters.get("accounting_item") and not account_details.get(filters.accounting_item):
		frappe.throw(_("Accounting item {0} does not exists").format(filters.accounting_item))

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))

def get_result(filters, account_details):
	gl_entries = get_gl_entries(filters)

	data = get_data_with_opening_closing(filters, account_details, gl_entries)

	result = get_result_as_list(data, filters)

	return result

def get_gl_entries(filters):
	select_fields = """, debit, credit"""

	order_by_statement = "order by posting_date, accounting_item"

	gl_entries = frappe.db.sql(
		"""
		select
			posting_date, accounting_item,
			reference_type, reference_name,
			link_doctype, link_docname
			{select_fields}
		from `tabGeneral Ledger Entry`
		where practitioner=%(practitioner)s {conditions}
		{order_by_statement}
		""".format(
			select_fields=select_fields, conditions=get_conditions(filters),
			order_by_statement=order_by_statement
		),
		filters, as_dict=1)

	return gl_entries


def get_conditions(filters):
	conditions = []
	if filters.get("accounting_item"):
		conditions.append("""accounting_item = '%s'""" % (filters.get("accounting_item")))

	if filters.get("reference_name"):
		conditions.append("reference_name=%(reference_name)s")

	if filters.get("link_docname"):
		conditions.append("link_docname=%(link_docname)s")

	from frappe.desk.reportview import build_match_conditions
	match_conditions = build_match_conditions("General Ledger Entry")

	if match_conditions:
		conditions.append(match_conditions)

	return "and {}".format(" and ".join(conditions)) if conditions else ""


def get_data_with_opening_closing(filters, account_details, gl_entries):
	data = []

	gle_map = initialize_gle_map(gl_entries, filters)

	totals, entries = get_accountwise_gle(filters, gl_entries, gle_map)

	# Opening for filtered account
	data.append(totals.opening)

	data += entries

	# totals
	data.append(totals.total)

	# closing
	data.append(totals.closing)

	return data

def get_totals_dict():
	def _get_debit_credit_dict(label):
		return _dict(
			accounting_item="'{0}'".format(label),
			debit=0.0,
			credit=0.0,
		)
	return _dict(
		opening = _get_debit_credit_dict(_('Opening')),
		total = _get_debit_credit_dict(_('Total')),
		closing = _get_debit_credit_dict(_('Closing (Opening + Total)'))
	)

def initialize_gle_map(gl_entries, filters):
	gle_map = frappe._dict()

	for gle in gl_entries:
		gle_map.setdefault(gle.get("reference_name"), _dict(totals=get_totals_dict(), entries=[]))
	return gle_map


def get_accountwise_gle(filters, gl_entries, gle_map):
	totals = get_totals_dict()
	entries = []

	def update_value_in_dict(data, key, gle):
		data[key].debit += flt(gle.debit)
		data[key].credit += flt(gle.credit)

	from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
	for gle in gl_entries:
		update_value_in_dict(gle_map[gle.get("reference_name")].totals, 'total', gle)
		update_value_in_dict(totals, 'total', gle)

		entries.append(gle)

		update_value_in_dict(gle_map[gle.get("reference_name")].totals, 'closing', gle)
		update_value_in_dict(totals, 'closing', gle)

	return totals, entries

def get_result_as_list(data, filters):
	balance = 0

	for d in data:
		if not d.get('posting_date'):
			balance = 0

		#if d.get('reference_type'):
		#	d['reference_type'] = _(d.get('reference_type'))

		#if d.get('link_doctype'):
		#	d['link_doctype'] = _(d.get('link_doctype'))

		balance = get_balance(d, balance, 'debit', 'credit')
		d['balance'] = balance

	return data

def get_balance(row, balance, debit_field, credit_field):
	balance += (row.get(debit_field, 0) -  row.get(credit_field, 0))

	return balance

def get_columns(filters):
	currency = "EUR"

	columns = [
		{
			"label": _("Posting Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 90
		},
		{
			"label": _("Accounting Item"),
			"fieldname": "accounting_item",
			"fieldtype": "Link",
			"options": "Accounting Item",
			"width": 180
		},
		{
			"label": _("Debit ({0})".format(currency)),
			"fieldname": "debit",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"label": _("Credit ({0})".format(currency)),
			"fieldname": "credit",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"label": _("Balance ({0})".format(currency)),
			"fieldname": "balance",
			"fieldtype": "Float",
			"width": 130
		}
	]

	columns.extend([
		{
			"label": _("Reference Type"),
			"fieldname": "reference_type",
			"width": 120
		},
		{
			"label": _("Reference Name"),
			"fieldname": "reference_name",
			"fieldtype": "Dynamic Link",
			"options": "reference_type",
			"width": 180
		},
		{
			"label": _("Posting Doctype"),
			"fieldname": "link_doctype",
			"width": 120
		},
		{
			"label": _("Posting Document Name"),
			"fieldname": "link_docname",
			"fieldtype": "Dynamic Link",
			"options": "link_doctype",
			"width": 180
		}
	])

	return columns