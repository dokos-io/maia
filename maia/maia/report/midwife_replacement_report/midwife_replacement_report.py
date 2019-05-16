# Copyright (c) 2017, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import (getdate, get_first_day, get_last_day, add_days, formatdate)

from maia.maia_accounting.utils import get_fiscal_year_data, get_fiscal_year
from maia.maia_accounting.doctype.accounting_item.accounting_item import get_accounts
from maia.maia_accounting.report.maia_profit_and_loss_statement.maia_profit_and_loss_statement import get_period_list, get_columns, \
	validate_fiscal_year, get_months, get_label, get_data

def execute(filters=None):
	currency = "EUR"

	period_list = get_period_list(filters.from_fiscal_year, filters.to_fiscal_year, filters.periodicity, filters.practitioner)
	practitioner_income = get_data(filters.practitioner, "Revenue", period_list)
	practitioner_social_security = get_third_party_payments(filters.practitioner, period_list)

	print(practitioner_social_security)
	if filters.practitioner:
		substitute = frappe.db.get_value("Professional Information Card", filters.practitioner, "substitute_practitioner")
		if substitute:
			substitute_income = get_data(substitute, "Revenue", period_list)

	receivable = []
	third_party_payment = []
	total_received = []

	data = []

	columns = get_columns(filters.periodicity, period_list, filters.practitioner)
	chart = get_chart_data(filters, columns, practitioner_income, receivable, third_party_payment, total_received)

	return columns, data, None, chart

	if filters.practitioner:
		practitioner = frappe.get_doc("Professional Information Card", filters.practitioner)

		if practitioner.substitute_first_name and practitioner.substitute_last_name and practitioner.substitute_start_date and practitioner.substitute_end_date:
			substitute_name = practitioner.substitute_first_name + " " + practitioner.substitute_last_name
			substitute_period_list = get_substitute_period_list(filters.from_fiscal_year, filters.to_fiscal_year, filters.periodicity, practitioner.substitute_start_date, practitioner.substitute_end_date, False)
		else:
			frappe.throw(_("Please make sure all replacement related fields are completed in this professional information card"))


	income = get_account_type_based_data(filters.company, "Income Account", period_list,
						 accumulated_values=False)

	income.update({
		"account_name": _("Income"),
		"parent_account": None,
		"indent": 0.0,
		"account": "Income",
		"currency": company_currency
	})

	if filters.practitioner:
		replacement_income = get_account_type_based_data(filters.company, "Income Account", substitute_period_list,
								 accumulated_values=False)

		replacement_income.update({
			"account_name": "'"+_("Replacement : {0}-{1}").format(formatdate(practitioner.substitute_start_date), formatdate(practitioner.substitute_end_date)) + "'",
			"parent_account": "Income",
			"indent": 1.0,
			"account": "Replacement Income",
			"currency": company_currency
		})


	if filters.practitioner and practitioner.mileage_allowance_excluded == 1:
		lump_sum_allowance = (frappe.get_all("Codification", filters={'lump_sum_travel_allowance': 1}, fields=["codification"]))
		lowland_allowance = (frappe.get_all("Codification", filters={'mileage_allowance_lowland': 1}, fields=["codification"]))
		mountain_allowance = (frappe.get_all("Codification", filters={'mileage_allowance_mountain': 1}, fields=["codification"]))
		walking_allowance = (frappe.get_all("Codification", filters={'mileage_allowance_walking_skiing': 1}, fields=["codification"]))
		items=[lump_sum_allowance, lowland_allowance, mountain_allowance, walking_allowance]

		item_list = []
		for i in items:
			for d in i:
				if d.codification not in item_list:
					item_list.append(d.codification)

		item_row = add_item_row(_("Mileage Allowances"), substitute_period_list, company_currency, filters.company, item_list)

		item_row.update({
			"account_name": "'"+_("Mileage Allowances : {0}-{1}").format(formatdate(practitioner.substitute_start_date), formatdate(practitioner.substitute_end_date)) + "'",
			"parent_account": "Income",
			"indent": 1.0,
			"account": "Mileage Allowance",
			"currency": company_currency
		})

	receivable = get_account_type_based_data(filters.company, "Receivable", period_list,
						 accumulated_values=False)

	receivable.update({
		"account_name": _("Receivables"),
		"parent_account": None,
		"indent": 0.0,
		"account": "Account Receivable",
		"currency": company_currency
	})

	if filters.practitioner:
		replacement_receivable = get_account_type_based_data(filters.company, "Receivable", substitute_period_list,
									 accumulated_values=False)

		replacement_receivable.update({
			"account_name": "'"+_("Replacement : {0}-{1}").format(formatdate(practitioner.substitute_start_date), formatdate(practitioner.substitute_end_date)) + "'",
			"parent_account": "Account Receivable",
			"indent": 1.0,
			"account": "Replacement Account Receivable",
			"currency": company_currency
		})

	third_party_payment = get_outstanding_social_security_data(filters.company, period_list,
								   accumulated_values=False)

	third_party_payment.update({
		"account_name": _("Third Party Payments"),
		"parent_account": None,
		"indent": 0.0,
		"account": "Third Party Payments",
		"currency": company_currency
	})

	if filters.practitioner:
		replacement_third_party_payment = get_outstanding_social_security_data(filters.company, substitute_period_list,
											   accumulated_values=False)

		replacement_third_party_payment.update({
			"account_name": "'"+_("Replacement : {0}-{1}").format(formatdate(practitioner.substitute_start_date), formatdate(practitioner.substitute_end_date)) + "'",
			"parent_account": "Third Party Payments",
			"indent": 1.0,
			"account": "Replacement Third Party Payments",
			"currency": company_currency
		})


	data = []
	data.append(income or {})
	if filters.practitioner:
		data.append(replacement_income or {})
		if practitioner.mileage_allowance_excluded:
			data.append(item_row or {})
	data.append(receivable or {})
	if filters.practitioner:
		data.append(replacement_receivable or {})

	total_received = add_total_row_account(data, data, _("Total Received"), period_list, company_currency)
	total_received.update({
		"account": "Total Received"
	})

	total_received_replacement = add_total_replacement_row(data, data, _("Total Replacement"), period_list, company_currency)
	total_received_replacement.update({
		"parent_account": "Total Received",
		"indent": 1.0,
		"account": "Total Replacement",
		"currency": company_currency
	})


	data.append(third_party_payment or {})
	if filters.practitioner:
		data.append(replacement_third_party_payment or {})
	data.append({})
	data.append(total_received)

	if filters.practitioner:
		data.append(total_received_replacement)
		data.append({})

		practicioner_part = total_practitioner(data, data, practitioner.name, substitute_period_list, company_currency, (practitioner.fee_percentage/100), practitioner.maximum_fee)
		replacement_fee = total_fee(data, data, substitute_name, substitute_period_list, company_currency, (practitioner.fee_percentage/100), practitioner.maximum_fee)

		data.append(practicioner_part)
		data.append(replacement_fee)


	columns = get_columns(filters.periodicity, period_list, filters.company)

	chart = get_chart_data(filters, columns, income, receivable, third_party_payment, total_received)

	return columns, data, None, chart

def get_third_party_payments(practitioner, period_list):
	data = {}
	total = 0

	third_parties = tuple([x['name'] for x in frappe.get_all("Party", filters={"is_social_contribution": 1})])

	for period in period_list:
		print(third_parties, practitioner, getdate(period['from_date']), getdate(period['to_date']))
		gl_sum = frappe.db.sql_list("""
			SELECT IFNULL(SUM(gl.debit - gl.credit), 0)
			FROM `tabPayment` pay
			LEFT JOIN `tabGeneral Ledger Entry` gl
			ON gl.link_docname = pay.name
			WHERE pay.party in (%s)
			AND pay.practitioner = %s
			AND pay.payment_date >= %s AND pay.payment_date <= %s
			AND gl.reference_type != 'Payment'
		""", (third_parties, practitioner, getdate(period['from_date']), getdate(period['to_date'])))

		print(gl_sum)
		if gl_sum and gl_sum[0]:
			amount = gl_sum[0]
		else:
			amount = 0

		total += amount
		data.setdefault(period["key"], amount)

	data["total"] = total
	return data



def add_total_row_account(out, data, label, period_list, currency):
	total_row = {
		"account_name": "'" + _("{0}").format(label) + "'",
		"account": "'" + _("{0}").format(label) + "'",
		"currency": currency
	}
	for row in data:
		if row.get("parent_account") == None and row.get("account") != "Third Party Payments":
			for period in period_list:
				total_row.setdefault(period.key, 0.0)
				total_row[period.key] += row.get(period.key, 0.0)


			total_row.setdefault("total", 0.0)
			total_row["total"] += row["total"]

	return total_row

def add_total_replacement_row(out, data, label, period_list, currency):
	total_row = {
		"account_name": "'" + _("{0}").format(label) + "'",
		"account": "'" + _("{0}").format(label) + "'",
		"currency": currency
	}
	for row in data:
		if row.get("parent_account") and row.get("account") != "Third Party Payments" and row.get("account") != "Mileage Allowance":
			for period in period_list:
				total_row.setdefault(period.key, 0.0)
				total_row[period.key] += row.get(period.key, 0.0)

		if row.get("account") == "Mileage Allowance":
			for period in period_list:
				total_row[period.key] -= row.get(period.key, 0.0)


	return total_row

def total_fee(out, data, label, period_list, currency, fee, maximum):
	total_row = {
		"account_name": "'" + _("{0}").format(label) + "'",
		"account": "'" + _("{0}").format(label) + "'",
		"currency": currency
	}
	for row in data:
		if row.get("account") == "Total Replacement":
			for period in period_list:
				total_row.setdefault(period.key, 0.0)
				total_row[period.key] += row.get(period.key, 0.0)


				if (total_row[period.key] * fee) > maximum:
					total_row[period.key] = total_row[period.key] - maximum

				else:
					total_row[period.key] = (total_row[period.key] * (1 - fee))


	return total_row

def total_practitioner(out, data, label, period_list, currency, fee, maximum):
	total_row = {
		"account_name": "'" + _("{0}").format(label) + "'",
		"account": "'" + _("{0}").format(label) + "'",
		"currency": currency
	}
	for row in data:
		if row.get("account") == "Total Replacement":
			for period in period_list:
				total_row.setdefault(period.key, 0.0)
				total_row[period.key] += (row.get(period.key, 0.0) * fee)

				if total_row[period.key] > maximum:
					total_row[period.key] = maximum

	return total_row

def get_chart_data(filters, columns, income, receivable, third_party_payments, total_received):
	labels = [d.get("label") for d in columns[2:]]

	income_data, receivable_data, third_party_payments_data, total_received_data = [], [], [], []
	for p in columns[2:]:
		if income:
			income_data.append(income[-2].get(p.get("fieldname")))
		if receivable:
			receivable_data.append(receivable.get(p.get("fieldname")))
		if third_party_payments:
			third_party_payments_data.append(third_party_payments.get(p.get("fieldname")))
		if total_received:
			total_received_data.append(total_received.get(p.get("fieldname")))

	datasets = []
	if income_data:
		datasets.append({'title': 'Income', 'values': income_data})
	if receivable_data:
		datasets.append({'title': 'Receivables', 'values': receivable_data})
	if third_party_payments_data:
		datasets.append({'title': 'Third Party Payments', 'values': third_party_payments_data})
	if total_received_data:
		datasets.append({'title': 'Total Received', 'values': total_received_data})

	chart = {
		"data": {
			'labels': labels,
			'datasets': datasets
			}
		}

	if not filters.accumulated_values:
		chart["type"] = "bar"
	else:
		chart["type"] = "line"

	return chart

def get_substitute_period_list(from_fiscal_year, to_fiscal_year, periodicity, from_date, end_date, accumulated_values=False, company=None):
	"""Get a list of dict {"from_date": from_date, "to_date": to_date, "key": key, "label": label}
Periodicity can be (Yearly, Quarterly, Monthly)"""

	fiscal_year = get_fiscal_year_data(from_fiscal_year, to_fiscal_year)
	validate_fiscal_year(fiscal_year, from_fiscal_year, to_fiscal_year)

	# start with first day, so as to avoid year to_dates like 2-April if ever they occur]
	year_start_date = getdate(fiscal_year.year_start_date)
	year_end_date = getdate(fiscal_year.year_end_date)

	months_to_add = {
		"Yearly": 12,
		"Half-Yearly": 6,
		"Quarterly": 3,
		"Monthly": 1
	}[periodicity]

	period_list = []

	start_date = from_date
	months = get_months(year_start_date, year_end_date)

	for i in range(months / months_to_add):
		period = frappe._dict({
			"from_date": start_date
		})

		to_date = add_days(get_last_day(start_date), 1)
		start_date = to_date

		if to_date == get_first_day(to_date):
			# if to_date is the first day, get the last day of previous month
			to_date = add_days(to_date, -1)

		if to_date <= end_date:
			# the normal case
			period.to_date = to_date
		else:
			# if a fiscal year ends before a 12 month period
			period.to_date = end_date

		period.to_date_fiscal_year = get_date_fiscal_year(period.to_date, company)

		period_list.append(period)

		if period.to_date == end_date:
			break

	# common processing
	for opts in period_list:
		key = opts["to_date"].strftime("%b_%Y").lower()
		if periodicity == "Monthly" and not accumulated_values:
			label = formatdate(opts["to_date"], "MMM YYYY")
		else:
			if not accumulated_values:
				label = get_label(periodicity, opts["from_date"], opts["to_date"])
			else:
				label = get_label(periodicity, period_list[0]["from_date"], opts["to_date"])

		opts.update({
			"key": key.replace(" ", "_").replace("-", "_"),
			"label": label,
			"year_start_date": year_start_date,
			"year_end_date": year_end_date
		})

	return period_list

def get_date_fiscal_year(date, company):
	from maia.maia_accounting.utils import get_fiscal_year
	return get_fiscal_year(date, practitioner=practitioner)[0]


def add_item_row(label, period_list, currency, company, items):
	item_row = {
		"account_name": "'" + _("{0}").format(label) + "'",
		"account": "'" + _("{0}").format(label) + "'",
		"currency": currency,
		"parent_account": "Income"
	}
	for i in items:
		for period in period_list:
			from_date = period.from_date
			to_date = period.to_date

			item_row.setdefault(period.key, 0.0)

			mileageall = get_mileage_allowance(company, from_date, to_date, i)
			if mileageall[0].mileage is not None:
				item_row[period.key] += mileageall[0].mileage

	return item_row


def get_mileage_allowance(company, from_date, to_date, item_code):
	return frappe.db.sql("""select sum(si_item.base_net_amount) as mileage from `tabSales Invoice` si, `tabSales Invoice Item` si_item
	where si.name = si_item.parent and si.docstatus = 1 and company=%s and si.posting_date>=%s and si.posting_date<=%s
	and si_item.item_code=%s""",(company, from_date, to_date, item_code), as_dict=True)
