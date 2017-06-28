# Copyright (c) 2017, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.accounts.report.financial_statements import (get_period_list, get_columns, get_fiscal_year_data, validate_fiscal_year, get_months, get_label)
from erpnext.accounts.report.cash_flow.cash_flow import get_account_type_based_data
from erpnext.accounts.utils import get_fiscal_year
from frappe.utils import (flt, getdate, get_first_day, get_last_day, date_diff,
                          add_months, add_days, formatdate, cint)

def execute(filters=None):
        
        company_currency = frappe.db.get_value("Company", filters.company, "default_currency")

        if filters.practicioner:
                practicioner = frappe.get_doc("Professional Information Card", filters.practicioner)

                if practicioner.substitute_first_name and practicioner.substitute_last_name and practicioner.substitute_start_date and practicioner.substitute_end_date:
                        substitute_name = practicioner.substitute_first_name + " " + practicioner.substitute_last_name

                        substitute_period_list = get_substitute_period_list(filters.from_fiscal_year, filters.to_fiscal_year, filters.periodicity, practicioner.substitute_start_date, practicioner.substitute_end_date, filters.accumulated_values, filters.company)

                else:
                        frappe.throw(_("Please make sure all replacement related fields are completed in this Professional Information Card"))
                
        period_list = get_period_list(filters.from_fiscal_year, filters.to_fiscal_year,
                                      filters.periodicity, filters.accumulated_values, filters.company)
        
        income = get_account_type_based_data(filters.company, "Income Account", period_list,
                          accumulated_values=filters.accumulated_values)

        income.update({
                "account_name": _("Income"),
                "parent_account": None,
                "indent": 0.0,
                "account": "Income",
                "currency": company_currency
        })

        if filters.practicioner:
                replacement_income = get_account_type_based_data(filters.company, "Income Account", substitute_period_list,
                          accumulated_values=filters.accumulated_values)

                replacement_income.update({
                        "account_name": "'"+_("Replacement : {0}-{1}").format(formatdate(practicioner.substitute_start_date), formatdate(practicioner.substitute_end_date)) + "'",
                        "parent_account": "Income",
                        "indent": 1.0,
                        "account": "Replacement Income",
                        "currency": company_currency
                })


        if filters.practicioner and practicioner.mileage_allowance_excluded == 1:
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
                        "account_name": "'"+_("Mileage Allowances : {0}-{1}").format(formatdate(practicioner.substitute_start_date), formatdate(practicioner.substitute_end_date)) + "'",
                        "parent_account": "Income",
                        "indent": 1.0,
                        "account": "Mileage Allowance",
                        "currency": company_currency
                })
                
        receivable = get_account_type_based_data(filters.company, "Receivable", period_list,
                          accumulated_values=filters.accumulated_values)

        receivable.update({
                "account_name": _("Receivables"),
                "parent_account": None,
                "indent": 0.0,
                "account": "Account Receivable",
                "currency": company_currency
        })

        if filters.practicioner:
                replacement_receivable = get_account_type_based_data(filters.company, "Receivable", substitute_period_list,
                          accumulated_values=filters.accumulated_values)

                replacement_receivable.update({
                        "account_name": "'"+_("Replacement : {0}-{1}").format(formatdate(practicioner.substitute_start_date), formatdate(practicioner.substitute_end_date)) + "'",
                        "parent_account": "Account Receivable",
                        "indent": 1.0,
                        "account": "Replacement Account Receivable",
                        "currency": company_currency
                })      
        
        third_party_payment = get_outstanding_social_security_data(filters.company, period_list,
                          accumulated_values=filters.accumulated_values)

        third_party_payment.update({
                "account_name": _("Third Party Payments"),
                "parent_account": None,
                "indent": 0.0,
                "account": "Third Party Payments",
                "currency": company_currency
        })

        if filters.practicioner:
                replacement_third_party_payment = get_outstanding_social_security_data(filters.company, substitute_period_list,
                          accumulated_values=filters.accumulated_values)

                replacement_third_party_payment.update({
                        "account_name": "'"+_("Replacement : {0}-{1}").format(formatdate(practicioner.substitute_start_date), formatdate(practicioner.substitute_end_date)) + "'",
                        "parent_account": "Third Party Payments",
                        "indent": 1.0,
                        "account": "Replacement Third Party Payments",
                        "currency": company_currency
                })
        
        
        data = []
        data.append(income or {})
        if filters.practicioner:
                data.append(replacement_income or {})
                if practicioner.mileage_allowance_excluded:
                        data.append(item_row or {})
        data.append(receivable or {})
        if filters.practicioner:
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
        if filters.practicioner:
                data.append(replacement_third_party_payment or {})
        data.append({})
        data.append(total_received)

        if filters.practicioner:
                data.append(total_received_replacement)
                data.append({})
                
                practicioner_part = total_practicioner(data, data, practicioner.name, substitute_period_list, company_currency, (practicioner.fee_percentage/100), practicioner.maximum_fee)
                replacement_fee = total_fee(data, data, substitute_name, substitute_period_list, company_currency, (practicioner.fee_percentage/100), practicioner.maximum_fee)

                data.append(practicioner_part)
                data.append(replacement_fee)


        columns = get_columns(filters.periodicity, period_list, filters.company)
        
        chart = get_chart_data(filters, columns, income, receivable, third_party_payment, total_received)
        
        return columns, data, None, chart

def get_outstanding_social_security_data(company, period_list, accumulated_values):
        data = {}
        total = 0
        for period in period_list:
                start_date = get_start_date(period, accumulated_values, company)
                gl_sum = frappe.db.sql_list("""
                select sum(credit) - sum(debit)
                from `tabGL Entry`
                where company=%s and posting_date >= %s and posting_date <= %s 
                and voucher_type != 'Period Closing Voucher'
                and party="CPAM"
                """, (company, start_date if accumulated_values else period['from_date'],
                      period['to_date']))

                if gl_sum and gl_sum[0]:
                        amount = gl_sum[0]
                else:
                        amount = 0

                total += amount
                data.setdefault(period["key"], amount)

        data["total"] = total
        return data


def get_start_date(period, accumulated_values, company):
        start_date = period["year_start_date"]
        if accumulated_values:
                start_date = get_fiscal_year(period.to_date, company=company)[1]

        return start_date



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

def total_practicioner(out, data, label, period_list, currency, fee, maximum):
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
        x_intervals = ['x'] + [d.get("label") for d in columns[2:]]

        income_data, receivable_data, third_party_payments_data, total_received_data = [], [], [], []
        for p in columns[2:]:
                if income:
                        income_data.append(income.get(p.get("fieldname")))
                if receivable:
                        receivable_data.append(receivable.get(p.get("fieldname")))
                if third_party_payments:
                        third_party_payments_data.append(third_party_payments.get(p.get("fieldname")))
                if total_received:
                        total_received_data.append(total_received.get(p.get("fieldname")))

        columns = [x_intervals]
        if income_data:
                columns.append([_("Income")] + income_data)
        if receivable_data:
                columns.append([_("Receivables")] + receivable_data)
        if third_party_payments_data:
                columns.append([_("Third Party Payments")] + third_party_payments_data)
        if total_received_data:
                columns.append([_("Total Received")] + total_received_data)

        chart = {
                "data": {
                        'x': 'x',
                        'columns': columns,
                        'colors': {
                                _('Income'): '#5E64FF',
                                _('Receivables'): '#b8c2cc',
                                _('Third Party Payments'): '#fff95e',
                                _('Total Received'): '#ff5858'
                        }
                }
        }

        if not filters.accumulated_values:
                chart["chart_type"] = "bar"

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

        for i in xrange(months / months_to_add):
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
        from erpnext.accounts.utils import get_fiscal_year
        return get_fiscal_year(date, company=company)[0]


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
