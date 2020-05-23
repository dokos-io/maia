# Copyright (c) 2013, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, getdate, get_first_day, add_months, add_days, formatdate
from frappe import _

from maia.maia_accounting.utils import get_fiscal_year_data, get_fiscal_year
from maia.maia_accounting.doctype.accounting_item.accounting_item import get_accounts

from six import itervalues

def execute(filters=None):
	period_list = get_period_list(filters.from_fiscal_year, filters.to_fiscal_year,
		filters.periodicity, filters.practitioner)

	income = get_data(filters.practitioner, "Revenue", period_list, filters = filters)
	
	expense = get_data(filters.practitioner, "Expense", period_list, filters=filters)
		
	net_profit_loss = get_net_profit_loss(income, expense, period_list)

	data = []
	data.extend(income or [])
	data.extend(expense or [])
	if net_profit_loss:
		data.append(net_profit_loss)

	columns = get_columns(filters.periodicity, period_list, filters.practitioner)

	chart = get_chart_data(filters, columns, income, expense, net_profit_loss)

	return columns, data, None, chart

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

	additional_conditions = get_additional_conditions(from_date, filters)

	accounts = [x["name"] for x in accounts]
	additional_conditions += " and accounting_item in ({})"\
		.format(", ".join([frappe.db.escape(d) for d in accounts]))

	gl_entries = frappe.db.sql("""select posting_date, accounting_item, debit, credit, currency
		from `tabGeneral Ledger Entry`
		where practitioner=%(practitioner)s
		{additional_conditions}
		and posting_date <= %(to_date)s
		and accounting_journal != "Closing entries"
		order by accounting_item, posting_date""".format(additional_conditions=additional_conditions),
		{
			"practitioner": practitioner,
			"from_date": from_date,
			"to_date": to_date
		},
		as_dict=True)

	for entry in gl_entries:
		gl_entries_by_account.setdefault(entry.accounting_item, []).append(entry)

	return gl_entries_by_account

def get_additional_conditions(from_date, filters):
	additional_conditions = []

	if from_date:
		additional_conditions.append("posting_date >= %(from_date)s")

	return " and {}".format(" and ".join(additional_conditions)) if additional_conditions else ""

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

				if entry.posting_date <= period.to_date and entry.posting_date >= period.from_date:
						d[period.key] = d.get(period.key, 0.0) + flt(entry.debit) - flt(entry.credit)

			if entry.posting_date < period_list[0].year_start_date:
				d["opening_balance"] = d.get("opening_balance", 0.0) + flt(entry.debit) - flt(entry.credit)

def prepare_data(accounts, account_type, period_list):
	data = []
	year_start_date = period_list[0]["year_start_date"].strftime("%Y-%m-%d")
	year_end_date = period_list[-1]["year_end_date"].strftime("%Y-%m-%d")

	for d in accounts:
		# add to output
		has_value = False
		total = 0
		row = frappe._dict({
			"account": _(d.name),
			"parent_account": _(account_type),
			"year_start_date": year_start_date,
			"year_end_date": year_end_date,
			"currency": "EUR",
			"opening_balance": d.get("opening_balance", 0.0) * (1 if account_type=="Expense" else -1),
			"account_name": ('%s - %s' %(_(d.accounting_number), _(d.name))
				if d.accounting_number else _(d.name))
		})
		for period in period_list:
			if d.get(period.key) and account_type == "Revenue":
				# change sign based on Debit or Credit, since calculation is done using (debit - credit)
				d[period.key] *= -1

			row[period.key] = flt(d.get(period.key, 0.0), 3)

			if abs(row[period.key]) >= 0.005:
				# ignore zero values
				has_value = True
				total += flt(row[period.key])

		row["has_value"] = has_value
		row["total"] = total
		data.append(row)

	return data

def filter_out_zero_value_rows(data, show_zero_values=False):
	data_with_value = []
	for d in data:
		if show_zero_values or d.get("has_value"):
			data_with_value.append(d)

	return data_with_value

def add_total_row(out, account_type, period_list):
	total_row = {
		"account_name": _("Total {0}").format(_(account_type)),
		"account": _("Total {0}").format(_(account_type)),
		"currency": "EUR"
	}

	for row in out:
		if row.get("parent_account"):
			for period in period_list:
				total_row.setdefault(period.key, 0.0)
				total_row[period.key] += row.get(period.key, 0.0)
				row[period.key] = row.get(period.key, 0.0)

			total_row.setdefault("total", 0.0)
			total_row["total"] += flt(row["total"])
			row["total"] = ""

	if "total" in total_row:
		out.append(total_row)

		# blank row after Total
		out.append({})

def get_net_profit_loss(income, expense, period_list):
	total = 0
	net_profit_loss = {
		"account_name": _("Profit for the year"),
		"account": _("Profit for the year"),
		"warn_if_negative": True,
		"currency": "EUR"
	}

	has_value = False

	for period in period_list:
		key = period.key
		total_income = flt(income[-2][key], 3) if income else 0
		total_expense = flt(expense[-2][key], 3) if expense else 0

		net_profit_loss[key] = total_income - total_expense

		if net_profit_loss[key]:
			has_value=True

		total += flt(net_profit_loss[key])
		net_profit_loss["total"] = total

	if has_value:
		return net_profit_loss

def get_chart_data(filters, columns, income, expense, net_profit_loss):
	labels = [d.get("label") for d in columns[2:]]

	income_data, expense_data, net_profit = [], [], []

	for p in columns[2:]:
		if income:
			income_data.append(income[-2].get(p.get("fieldname")))
		if expense:
			expense_data.append(expense[-2].get(p.get("fieldname")))
		if net_profit_loss:
			net_profit.append(net_profit_loss.get(p.get("fieldname")))

	datasets = []
	if income_data:
		datasets.append({'name': _('Income'), 'values': income_data})
	if expense_data:
		datasets.append({'name': _('Expense'), 'values': expense_data})
	if net_profit:
		datasets.append({'name': _('Net Profit/Loss'), 'values': net_profit})

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

def get_period_list(from_fiscal_year, to_fiscal_year, periodicity, practitioner=None):
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

	start_date = year_start_date
	months = get_months(year_start_date, year_end_date)

	for i in range(months // months_to_add):
		period = frappe._dict({
			"from_date": start_date
		})

		to_date = add_months(start_date, months_to_add)
		start_date = to_date

		if to_date == get_first_day(to_date):
			# if to_date is the first day, get the last day of previous month
			to_date = add_days(to_date, -1)

		if to_date <= year_end_date:
			# the normal case
			period.to_date = to_date
		else:
			# if a fiscal year ends before a 12 month period
			period.to_date = year_end_date

		period.to_date_fiscal_year = get_fiscal_year(period.to_date, practitioner=practitioner)[0]
		period.from_date_fiscal_year_start_date = get_fiscal_year(period.from_date, practitioner=practitioner)[1]

		period_list.append(period)

		if period.to_date == year_end_date:
			break

	# common processing
	for opts in period_list:
		key = opts["to_date"].strftime("%b_%Y").lower()
		if periodicity == "Monthly":
			label = formatdate(opts["to_date"], "MMM YYYY")
		else:
			label = get_label(periodicity, opts["from_date"], opts["to_date"])

		opts.update({
			"key": key.replace(" ", "_").replace("-", "_"),
			"label": label,
			"year_start_date": year_start_date,
			"year_end_date": year_end_date
		})

	return period_list

def validate_fiscal_year(fiscal_year, from_fiscal_year, to_fiscal_year):
	if not fiscal_year.get('year_start_date') and not fiscal_year.get('year_end_date'):
		frappe.throw(_("End Year cannot be before Start Year"))

def get_months(start_date, end_date):
	diff = (12 * end_date.year + end_date.month) - (12 * start_date.year + start_date.month)
	return diff + 1


def get_label(periodicity, from_date, to_date):
	if periodicity == "Yearly":
		if formatdate(from_date, "YYYY") == formatdate(to_date, "YYYY"):
			label = formatdate(from_date, "YYYY")
		else:
			label = formatdate(from_date, "YYYY") + "-" + formatdate(to_date, "YYYY")
	else:
		label = formatdate(from_date, "MMM YY") + "-" + formatdate(to_date, "MMM YY")

	return label

def get_columns(periodicity, period_list, practitioner=None):
	columns = [{
		"fieldname": "account",
		"label": _("Accounting Item"),
		"fieldtype": "Link",
		"options": "Accounting Item",
		"width": 300
	}]
	if practitioner:
		columns.append({
			"fieldname": "currency",
			"label": _("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"hidden": 1
		})
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