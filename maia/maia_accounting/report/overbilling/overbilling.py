# Copyright (c) 2013, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import maia
from frappe import _
from frappe.utils import (getdate, get_first_day, get_last_day, add_days, formatdate, flt)

from maia.maia_accounting.utils import get_fiscal_year_data, get_fiscal_year
from maia.maia_accounting.doctype.accounting_item.accounting_item import get_accounts
from maia.maia_accounting.report.maia_profit_and_loss_statement.maia_profit_and_loss_statement import get_period_list, get_columns, \
	validate_fiscal_year, get_months, get_label
from collections import defaultdict

def execute(filters=None):
	period_list = get_period_list(filters.from_fiscal_year, filters.to_fiscal_year, filters.periodicity, filters.practitioner)

	if not filters.practitioner:
		frappe.throw(_("Please select a practitioner"))

	data = get_data(filters.practitioner, period_list)
	columns = get_columns(filters.periodicity, period_list, filters.practitioner)

	return columns, data

def get_data(practitioner, period_list):
	output = {}
	period_total = 0
	for period in period_list:
		paid_invoices = frappe.get_all("Revenue",
			filters={
				"transaction_date": ["between", [period.get("from_date"), period.get("to_date")]],
				"status": "Paid",
				"docstatus": 1,
				"practitioner": practitioner
			},
			fields=["name", "consultation_type", "consultation"])

		consultations = defaultdict(list)
		for paid_invoice in paid_invoices:
			if paid_invoice.consultation:
				consultations[paid_invoice.consultation_type].append(paid_invoice.consultation)

		total = 0
		for dt, values in consultations.items():
			data = frappe.get_all("Consultation Items",
				filters={"parenttype": dt, "parent": ["in", values]}, \
				fields=["codification", "sum(overbilling) as overbilling"])

			if data:
				total += flt(data[0]["overbilling"])

		period_total += total
		output.update({period.key: total})

	output.update({"total": period_total})
	return [output]

def get_columns(periodicity, period_list, practitioner=None):
	columns = []

	for period in period_list:
		columns.append({
			"fieldname": period.key,
			"label": period.label,
			"fieldtype": "Currency",
			"options": "currency",
			"width": 150
		})
	if periodicity!="Yearly":
		columns.append({
			"fieldname": "total",
			"label": _("Total"),
			"fieldtype": "Currency",
			"width": 150
		})

	return columns