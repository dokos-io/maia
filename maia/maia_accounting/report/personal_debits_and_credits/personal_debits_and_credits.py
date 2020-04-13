# Copyright (c) 2020, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from maia.maia_accounting.report.maia_profit_and_loss_statement.maia_profit_and_loss_statement import get_period_list

def execute(filters=None):
	if not filters.fiscal_year:
		frappe.throw(_("Please select a fiscal year"))
	
	if not filters.practitioner:
		frappe.throw(_("Please select a practitioner"))

	data = get_data(filters)

	columns = get_columns()
	return columns, data

def get_data(filters=None):
	fiscal_year = frappe.db.get_value("Maia Fiscal Year", filters.fiscal_year, ["year_start_date", "year_end_date"])
	bank_accounts = get_bank_accounts()
	personal_accounts = get_personal_accounts()

	references = frappe.get_all("General Ledger Entry",
		filters={
		"posting_date": ("between", fiscal_year),
		"practitioner": filters.practitioner
		},
		fields=["name", "accounting_item", "posting_date", "link_doctype", "link_docname"]
	)

	output = []
	for dt in ["Payment", "Miscellaneous Operation"]:
		data = []
		docnames = [x.link_docname for x in references if x.link_doctype==dt]
		description_field = "party as description" if dt == "Payment" else "title as description"
		values = frappe.get_all(dt, filters={"name": ("in", docnames), "docstatus": 1}, fields=["name", description_field], debug=True)

		query_filters = {
			"link_doctype": dt,
			"link_docname": ("in",  [x.name for x in values]),
			"accounting_item": ("in", personal_accounts)
		}
		query_fields=["name", "accounting_item", "posting_date", "link_doctype", "link_docname"]

		if filters.debit_credit == "Debits":
			query_filters["debit"] = (">", 0)
			query_fields.append("debit as amount")
		else:
			query_filters["credit"] = (">", 0)
			query_fields.append("credit as amount")
	
		data += frappe.get_all("General Ledger Entry",
			filters=query_filters,
			fields=query_fields
		)

		for d in data:
			d["description"] = [x.description for x in values if x.name == d.link_docname][0]

		output += data

	return output


def get_bank_accounts():
	payment_methods = frappe.get_all("Payment Method", fields=["bank_account", "accounting_item"])

	output = set()
	for payment_method in payment_methods:
		if payment_method.accounting_item:
			output.add(payment_method.accounting_item)
		elif payment_method.bank_account:
			bank_item = frappe.db.get_value("Maia Bank Account", payment_method.bank_account, "accounting_item")
			if bank_item:
				output.add(bank_item)

	return list(output)

def get_personal_accounts():
	return [x.name for x in frappe.get_all("Accounting Item", filters={"accounting_item_type": "Practitioner"})]

def get_columns():
	currency = "EUR"
	columns = [
		{
			"label": _("Date"),
			"fieldname": "posting_date",
			"fieldtype": "date",
			"width": 140
		},
		{
			"label": _("Amount ({0})".format(currency)),
			"fieldname": "amount",
			"fieldtype": "Float",
			"width": 150
		},
		{
			"label": _("Linked Doctype"),
			"fieldname": "link_doctype",
			"fieldtype": "Link",
			"options": "DocType",
			"width": 200
		},
		{
			"label": _("Linked Documents"),
			"fieldname": "link_docname",
			"fieldtype": "Dynamic Link",
			"options": "link_doctype",
			"width": 200
		},
		{
			"label": _("Description"),
			"fieldname": "description",
			"fieldtype": "Data",
			"width": 200
		}
	]

	return columns