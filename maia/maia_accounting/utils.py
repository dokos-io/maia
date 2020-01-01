# -*- coding: utf-8 -*-
# Copyright (c) 2019, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, cstr, formatdate, nowdate, add_days, add_years
import maia

class FiscalYearError(frappe.ValidationError): pass

def get_fiscal_year_data(from_fiscal_year, to_fiscal_year):
	fiscal_year = frappe.db.sql("""select min(year_start_date) as year_start_date,
		max(year_end_date) as year_end_date from `tabMaia Fiscal Year` where
		name between %(from_fiscal_year)s and %(to_fiscal_year)s""",
		{'from_fiscal_year': from_fiscal_year, 'to_fiscal_year': to_fiscal_year}, as_dict=1)

	return fiscal_year[0] if fiscal_year else {}

@frappe.whitelist()
def get_fiscal_year(date=None, fiscal_year=None, label="Date", practitioner=None, verbose=1, as_dict=False):
	return get_fiscal_years(date, fiscal_year, label, practitioner, verbose, as_dict=as_dict)[0]

def get_fiscal_years(transaction_date=None, fiscal_year=None, label="Date", practitioner=None, verbose=1, as_dict=False):
	fiscal_years = frappe.cache().hget("fiscal_years", practitioner) or []

	if not fiscal_years:
		# if year start date is 2012-04-01, year end date should be 2013-03-31 (hence subdate)
		cond = ""
		if fiscal_year:
			cond += " and fy.name = {0}".format(frappe.db.escape(fiscal_year))

		fiscal_years = frappe.db.sql("""
			select
				fy.name, fy.year_start_date, fy.year_end_date
			from
				`tabMaia Fiscal Year` fy
			where
				disabled = 0 {0}
			order by
				fy.year_start_date desc""".format(cond), as_dict=True)

		frappe.cache().hset("fiscal_years", practitioner, fiscal_years)

	if transaction_date:
		transaction_date = getdate(transaction_date)

	for fy in fiscal_years:
		matched = False
		if fiscal_year and fy.name == fiscal_year:
			matched = True

		if (transaction_date and getdate(fy.year_start_date) <= transaction_date
			and getdate(fy.year_end_date) >= transaction_date):
			matched = True

		if matched:
			if as_dict:
				return (fy,)
			else:
				return ((fy.name, fy.year_start_date, fy.year_end_date),)

	error_msg = _("""{0} {1} not in any active Fiscal Year.""").format(label, formatdate(transaction_date))
	if verbose==1: frappe.msgprint(error_msg)
	raise FiscalYearError(error_msg)

@frappe.whitelist()
def auto_create_fiscal_year():
	for d in frappe.db.sql("""select name from `tabMaia Fiscal Year` where year_end_date = date_add(current_date, interval 3 day)"""):
		try:
			current_fy = frappe.get_doc("Maia Fiscal Year", d[0])

			new_fy = frappe.copy_doc(current_fy, ignore_no_copy=False)

			new_fy.year_start_date = add_days(current_fy.year_end_date, 1)
			new_fy.year_end_date = add_years(current_fy.year_end_date, 1)

			start_year = cstr(new_fy.year_start_date.year)
			end_year = cstr(new_fy.year_end_date.year)
			new_fy.year = start_year if start_year==end_year else (start_year + "-" + end_year)
			new_fy.auto_created = 1

			new_fy.insert(ignore_permissions=True)
		except frappe.NameError:
			pass

@frappe.whitelist()
def get_balance_on(account=None, date=None, practitioner=None):
	if not account and frappe.form_dict.get("account"):
		account = frappe.form_dict.get("account")
	if not date and frappe.form_dict.get("date"):
		date = frappe.form_dict.get("date")

	cond = []
	if date:
		cond.append("posting_date <= %s" % frappe.db.escape(cstr(date)))
	else:
		# get balance of all entries that exist
		date = nowdate()

	try:
		year_start_date = get_fiscal_year(date, verbose=0)[1]
	except FiscalYearError:
		if getdate(date) > getdate(nowdate()):
			# if fiscal year not found and the date is greater than today
			# get fiscal year for today's date and its corresponding year start date
			year_start_date = get_fiscal_year(nowdate(), verbose=1)[1]
		else:
			# this indicates that it is a date older than any existing fiscal year.
			# hence, assuming balance as 0.0
			return 0.0

	if account:

		acc = frappe.get_doc("Accounting Item", account)

		if not frappe.flags.ignore_account_permission:
			acc.check_permission("read")

		if acc.is_revenue_item() or acc.is_expense_item():
			cond.append("posting_date >= '%s'" % year_start_date)

		cond.append("""gle.accounting_item = %s """ % (frappe.db.escape(account, percent=False), ))

	if practitioner:
		cond.append("""gle.practitioner = %s """ % (frappe.db.escape(practitioner, percent=False)))

	if account:
		select_field = "sum(debit) - sum(credit)"
		bal = frappe.db.sql("""
			SELECT {0}
			FROM `tabGeneral Ledger Entry` gle
			WHERE {1}""".format(select_field, " and ".join(cond)))[0][0]

		# if bal is None, return 0
		return flt(bal)

def has_accounting_permissions(doc, ptype, user):
	if "System Manager" in frappe.get_roles(user):
		return True

	return doc.owner==user or doc.practitioner==maia.get_practitioner(user)

def get_accounting_query_conditions(doctype, user):
	if not user: user = frappe.session.user

	if user=="Administrator" or "System Manager" in frappe.get_roles(user):
		return ""
	
	return """(`tab{doctype}`.owner="{user}" or `tab{doctype}`.practitioner="{practitioner}")""".format(doctype=doctype, user=user, practitioner=maia.get_practitioner(user))

def get_outstanding(practitioner, parties=None):

	party_filter = ["in", tuple(parties)] if parties else ""

	outstanding = frappe.get_all("Revenue", filters={"docstatus": 1, "practitioner": practitioner, \
		"party": party_filter, "status": "Unpaid"}, fields=["SUM(outstanding_amount) as total"])

	if outstanding:
		return outstanding[0]["total"]
	else:
		return 0