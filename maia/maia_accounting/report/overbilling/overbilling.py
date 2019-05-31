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

def execute(filters=None):
	period_list = get_period_list(filters.from_fiscal_year, filters.to_fiscal_year, filters.periodicity, filters.practitioner)

	data = get_data(filters.practitioner)

	columns, data = [], []
	return columns, data

def get_data(practitioner):
	doctypes = maia.get_consultation_types()
	paid_invoices = [x["name"] for x in frappe.get_all("Revenue", filters={"transaction_date": ["between", ["2018-01-01", "2018-12-31"]], "status": "Paid"})]

	total = 0
	for doctype in doctypes:
		data = frappe.get_all(doctype, filters={"consultation_date": ["between", ["2018-01-01", "2018-12-31"]], "invoice": ["in", paid_invoices], "docstatus": 1}, \
			fields=["codification", "total_price", "without_codification"])

		for d in data:
			basic_price = frappe.db.get_value("Codification", d.codification, "basic_price")
			total += flt(d["total_price"]) - flt(d["without_codification"]) - flt(basic_price)
