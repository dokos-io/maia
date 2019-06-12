# Copyright (c) 2017, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import maia
from frappe import _
from frappe.utils import (getdate, get_first_day, get_last_day, add_days, formatdate, flt)

from maia.maia_accounting.utils import get_fiscal_year_data, get_fiscal_year
from maia.maia_accounting.doctype.accounting_item.accounting_item import get_accounts
from maia.maia_accounting.report.maia_profit_and_loss_statement.maia_profit_and_loss_statement import get_period_list, get_columns, \
	validate_fiscal_year, get_months, get_label, get_data

def execute(filters=None):
	currency = maia.get_default_currency()

	period_list = get_period_list(filters.from_fiscal_year, filters.to_fiscal_year, filters.periodicity, filters.practitioner)
	fiscal_year = get_fiscal_year_data(filters.from_fiscal_year, filters.to_fiscal_year)

	data = []
	datasets = []
	for replacement in frappe.get_all("Replacement", \
		filters={"start_date": [">=", fiscal_year.year_start_date], "end_date": ["<=", fiscal_year.year_end_date], "practitioner": filters.practitioner}, \
		fields=["*"]):

		data.extend(get_substitute_header(replacement))
		substitute_period_list = get_substitute_period_list(period_list, replacement)

		practitioner_income = get_data(replacement.substitute, "Revenue", substitute_period_list)

		if practitioner_income:
			retrocessions = calculate_retrocession(substitute_period_list, replacement, practitioner_income[-2], currency)

			data.extend(retrocessions)
			data.append({})

			datasets.append({'title': replacement.substitute, 'values': retrocessions[-1]})


	columns = get_report_columns(filters.periodicity, period_list)
	chart = get_chart_data(filters, columns, datasets)

	return columns, data, None, chart

def get_report_columns(periodicity, period_list):
	columns = get_columns(periodicity, period_list)

	for column in columns:
		if column["fieldname"] == "account":
			column["label"] = ""
			column["fieldtype"] = "Data"

	return columns

def get_chart_data(filters, columns, datasets):
	labels = [d.get("label") for d in columns[2:]]
	keys = [d.get("fieldname") for d in columns[2:]]

	for d in datasets:
		keep = []
		for key in keys:
			keep.append(d["values"][key] if key in d["values"] else 0)

		d["values"] = keep

	chart = {
		"data": {
			'labels': labels,
			'datasets': datasets
			},
		"type": "bar"
		}

	return chart

def get_substitute_header(replacement):
	return [{
		"account": replacement.substitute,
		"account_name": "substitute"
	},
	{
		"account": "{0} {1} {2}".format(formatdate(replacement.start_date), _("to"), formatdate(replacement.end_date)),
		"account_name": "dates"
	}]

def get_substitute_period_list(period_list, replacement):
	replacement_period_list = []

	for period in period_list:
		if period.to_date < replacement.start_date:
			continue
		if period.from_date > replacement.end_date:
			continue
		if period.to_date >= replacement.start_date and period.from_date <= replacement.start_date:
			period.from_date = replacement.start_date
		if period.to_date >= replacement.end_date and period.from_date <= replacement.end_date:
			period.to_date = replacement.end_date

		replacement_period_list.append(period)

	return replacement_period_list

def calculate_retrocession(period_list, replacement, income, currency):
	calculated_retrocession = dict(income)

	mileage_allowance = get_mileage_allowance(period_list, replacement.substitute, currency)

	mileage = mileage_allowance
	if not replacement.mileage_allowance_excluded:
		mileage = {}
		mileage_allowance["account"] = _("Mileage Allowances - Excluded")

	total = 0
	for period in period_list:
		retrocessions = (calculated_retrocession[period.key] - (mileage[period.key] if period.key in mileage else 0)) \
			* (1 - replacement.fee_percentage / 100)

		if replacement.maximum_fee > 0:
			retrocessions = min(retrocessions, replacement.maximum_fee)

		total += retrocessions
		calculated_retrocession[period.key] = retrocessions
		calculated_retrocession["account"] = _("Total Retrocession")
		calculated_retrocession["account_name"] = _("Total Retrocession")

	calculated_retrocession["total"] =  total

	r = []
	r.append(income)
	r.append(mileage_allowance)
	r.append(calculated_retrocession)

	return r

def get_mileage_allowance(period_list, practitioner, currency):
	result = {}
	result["account"] = _("Mileage Allowances")
	result["account_name"] = "mileage_allowances"
	result["currency"] = currency

	mileage_codifications = tuple(get_mileage_codifications())

	total_mileage = 0
	for period in period_list:
		total = frappe.db.sql("""
			SELECT SUM(ri.total_amount) as total,
			r.amount, r.outstanding_amount
			FROM `tabRevenue` r
			LEFT JOIN `tabRevenue Items` ri
			ON r.name = ri.parent
			WHERE r.docstatus = 1
			AND r.transaction_date >= '{from_date}'
			AND r.transaction_date <= '{to_date}'
			AND ri.codification in {codifications}
		""".format(
			codifications=mileage_codifications,
			from_date=period.from_date,
			to_date=period.to_date
			), as_dict=True)

		calculated_amount = (flt(total[0]["total"]) * ((flt(total[0]["amount"]) - flt(total[0]["outstanding_amount"])) / flt(total[0]["amount"]))) if (total and flt(total[0]["amount"]) != 0) else 0

		data = {period.key: calculated_amount}
		total_mileage += calculated_amount
		result.update(data)

	result["total"] = total_mileage
	return result

def get_mileage_codifications():
	return [x["name"] for x in frappe.db.sql("""
		SELECT name
		FROM `tabCodification`
		WHERE lump_sum_travel_allowance = 1
		OR mileage_allowance_lowland =1
		OR mileage_allowance_mountain = 1
		OR mileage_allowance_walking_skiing = 1
	""", as_dict=True)]