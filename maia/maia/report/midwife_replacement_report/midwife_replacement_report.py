# Copyright (c) 2017, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from erpnext.accounts.report.financial_statements import (get_period_list, get_columns)
from erpnext.accounts.report.cash_flow.cash_flow import get_account_type_based_data
from erpnext.accounts.utils import get_fiscal_year

def execute(filters=None):
        
        company_currency = frappe.db.get_value("Company", filters.company, "default_currency")
        practicioner = frappe.get_doc("Professional Information Card", filters.practicioner)
        substitute_name = practicioner.substitute_first_name + " " + practicioner.substitute_last_name

        
        period_list = get_period_list(filters.from_fiscal_year, filters.to_fiscal_year,
                                      filters.periodicity, filters.accumulated_values, filters.company)

        income = get_account_type_based_data(filters.company, "Income Account", period_list,
                          accumulated_values=filters.accumulated_values)

        income.update({
                "account_name": _("Income"),
                "parent_account": None,
                "indent": 0.0,
                "account": _("Income"),
                "currency": company_currency
        })

        receivable = get_account_type_based_data(filters.company, "Receivable", period_list,
                          accumulated_values=filters.accumulated_values)

        receivable.update({
                "account_name": _("Account Receivable"),
                "parent_account": None,
                "indent": 0.0,
                "account": _("Account Receivable"),
                "currency": company_currency
        })
        
        third_party_payment = get_outstanding_social_security_data(filters.company, period_list,
                          accumulated_values=filters.accumulated_values)

        third_party_payment.update({
                "account_name": _("Third Party Payments"),
                "parent_account": None,
                "indent": 0.0,
                "account": _("Third Party Payments"),
                "currency": company_currency
        })
        
        
        data = []
        data.append(income or [])
        data.append(receivable or [])
        
        total_received = add_total_row_account(data, data, _("Total Received"), period_list, company_currency)
        practicioner_part = total_practicioner(data, data, practicioner.name, period_list, company_currency, (practicioner.fee_percentage/100), practicioner.maximum_fee)
        replacement_fee = total_fee(data, data, substitute_name, period_list, company_currency, (practicioner.fee_percentage/100), practicioner.maximum_fee)
        
        data.append(third_party_payment or [])
        data.append([])
        data.append(total_received)

        data.append([])
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
        frappe.logger().debug(data)
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
                for period in period_list:
                        total_row.setdefault(period.key, 0.0)
                        total_row[period.key] += row.get(period.key, 0.0)

                        total_row.setdefault("total", 0.0)
                        total_row["total"] += row["total"]

        return total_row

def total_practicioner(out, data, label, period_list, currency, fee, maximum):
        total_row = {
                "account_name": "'" + _("{0}").format(label) + "'",
                "account": "'" + _("{0}").format(label) + "'",
                "currency": currency
        }
        for row in data:
                for period in period_list:
                        total_row.setdefault(period.key, 0.0)
                        total_row[period.key] += row.get(period.key, 0.0) - (row.get(period.key, 0.0) * fee)

                        if maximum != 0 or maximum is not None:
                                if (total_row[period.key] * fee) > maximum:
                                        total_row[period.key] = total_row[period.key] - maximum


                        total_row.setdefault("total", 0.0)
                        total_row["total"] += row["total"]

        return total_row

def total_fee(out, data, label, period_list, currency, fee, maximum):
        total_row = {
                "account_name": "'" + _("{0}").format(label) + "'",
                "account": "'" + _("{0}").format(label) + "'",
                "currency": currency
        }
        for row in data:
                for period in period_list:
                        total_row.setdefault(period.key, 0.0)
                        total_row[period.key] += (row.get(period.key, 0.0) * fee)

                        if maximum != 0 or maximum is not None:
                                if total_row[period.key] > maximum:
                                        total_row[period.key] = maximum
                        
                        total_row.setdefault("total", 0.0)
                        total_row["total"] += row["total"]

                        frappe.logger().debug(total_row["total"])

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
                columns.append([_("Receivable")] + receivable_data)
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
                                _('Receivable'): '#b8c2cc',
                                _('Third Party Payments'): '#fff95e',
                                _('Total Received'): '#ff5858'
                        }
                }
        }

        if not filters.accumulated_values:
                chart["chart_type"] = "bar"

        return chart
