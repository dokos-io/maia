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
	validate_fiscal_year, get_months, get_label, get_accounts, prepare_data, filter_out_zero_value_rows, \
	get_additional_conditions, add_total_row

from six import itervalues

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

		practitioner_income = get_data(replacement.practitioner, "Revenue", substitute_period_list)
		retroceeded_fee = get_fee_retrocessions(replacement.practitioner, substitute_period_list, currency)

		if practitioner_income:
			data_lines, calculated_retrocession = calculate_retrocession(substitute_period_list, replacement, practitioner_income[-2], currency)
			outstanding = calculate_outstanding(substitute_period_list, retroceeded_fee, calculated_retrocession, currency)

			data.extend(data_lines)
			data.append({})

			datasets.append({'title': replacement.substitute, 'values': data_lines[-1]})

		data.append(retroceeded_fee)
		if practitioner_income:
			data.append({})
			data.append(outstanding)

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

	return r, calculated_retrocession

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

def get_data(practitioner, account_type, period_list, filters=None, only_current_fiscal_year=True, total = True):

	accounts = get_accounts(account_type)
	accounts_by_name = {}
	for d in accounts:
		accounts_by_name[d.name] = d
	if not accounts:
		return None

	#accounts, accounts_by_name, parent_children_map = filter_accounts(accounts)

	gl_entries_by_account = {}
	
	set_gl_entries_by_account(
		practitioner,
		period_list[0]["year_start_date"] if only_current_fiscal_year else None,
		period_list[-1]["to_date"],
		accounts, filters,
		gl_entries_by_account
	)

	calculate_values(accounts_by_name, gl_entries_by_account, period_list)
	#accumulate_values_into_parents(accounts, accounts_by_name, period_list, accumulated_values)
	out = prepare_data(accounts, account_type, period_list)
	out = filter_out_zero_value_rows(out)

	if out and total:
		add_total_row(out, account_type, period_list)

	return out

def set_gl_entries_by_account(practitioner, from_date, to_date, accounts, filters, gl_entries_by_account):
	"""Returns a dict like { "account": [gl entries], ... }"""

	accounts = [x["name"] for x in accounts]
	additional_conditions = " and gle.accounting_item in ({})"\
		.format(", ".join([frappe.db.escape(d) for d in accounts]))

	gl_entries = frappe.db.sql("""select gle.posting_date,
		gle.accounting_item, gle.debit, gle.credit, gle.currency,
		rev.transaction_date
		from `tabGeneral Ledger Entry` gle
		left join `tabRevenue` rev
		on gle.reference_name = rev.name
		where rev.practitioner=%(practitioner)s
		{additional_conditions}
		and rev.transaction_date >= %(from_date)s
		and rev.transaction_date <= %(to_date)s
		and rev.docstatus=1
		and rev.status="Paid"
		order by gle.accounting_item, gle.posting_date""".format(additional_conditions=additional_conditions),
		{
			"practitioner": practitioner,
			"from_date": from_date,
			"to_date": to_date
		},
		as_dict=True)

	for entry in gl_entries:
		gl_entries_by_account.setdefault(entry.accounting_item, []).append(entry)

	return gl_entries_by_account

def calculate_values(accounts_by_name, gl_entries_by_account, period_list):
	for entries in itervalues(gl_entries_by_account):
		for entry in entries:
			d = accounts_by_name.get(entry.accounting_item)
			if not d:
				frappe.msgprint(
					_("Could not retrieve information for {0}.".format(entry.account)), title="Error",
					raise_exception=1
				)
			for period in period_list:
				# check if posting date is within the period

				if entry.transaction_date <= period.to_date and entry.transaction_date >= period.from_date:
						d[period.key] = d.get(period.key, 0.0) + flt(entry.debit) - flt(entry.credit)

			if entry.transaction_date < period_list[0].year_start_date:
				d["opening_balance"] = d.get("opening_balance", 0.0) + flt(entry.debit) - flt(entry.credit)

def get_fee_retrocessions(practitioner, substitute_period_list, currency):
	retrocession_accounts = [x.name for x in frappe.get_all("Accounting Item", filters={"code_2035": "AC"})]
	retrocessions = frappe.get_all("Miscellaneous Operation Items", filters={"accounting_item": ["in", retrocession_accounts]}, fields=["parent", "amount"])
	parents = [x.get("parent") for x in retrocessions]
	parents_with_dates = frappe.get_all("Miscellaneous Operation", filters={"name": ["in", parents]}, fields=["name", "posting_date"])

	total_retrocessions = 0
	result = {}
	result["account"] = _("Fee Retrocessions")
	result["account_name"] = _("Fee Retrocessions")
	result["currency"] = currency

	for period in substitute_period_list:
		filtered_parents = [x.name for x in parents_with_dates if getdate(x.get("posting_date")) >= period.get("from_date") and getdate(x.get("posting_date")) <= period.get("to_date")]
		calculated_amount = sum([x.get("amount") for x in retrocessions if x.get("parent") in filtered_parents]) * -1

		data = {period.key: calculated_amount}
		total_retrocessions += calculated_amount
		result.update(data)

	result["total"] = total_retrocessions

	return result

def calculate_outstanding(substitute_period_list, retroceeded_fee, calculated_retrocession, currency):
	total_outstanding = 0
	result = {}
	result["account"] = _("Outstanding Amount")
	result["account_name"] = _("Outstanding Amount")
	result["currency"] = currency

	for period in substitute_period_list:
		total_outstanding += calculated_retrocession.get(period.key)
		outstanding_amount = total_outstanding + retroceeded_fee.get(period.key)
		total_outstanding += retroceeded_fee.get(period.key)
		data = {period.key: outstanding_amount}
		result.update(data)

	result["total"] = total_outstanding

	return result