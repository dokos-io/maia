# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import now_datetime, getdate

def delete_expired_sms():
	data = frappe.get_all("SMS Reminder", fields=["name", "send_on"])

	for d in data:
		if d.send_on < now_datetime():
			frappe.delete_doc("SMS Reminder", d.name, ignore_permissions=True)

def reset_portal_doctypes():
	frappe.reload_doctype("Portal Settings")

	items = frappe.get_all("Portal Menu Item", fields=[
							'name', 'title', 'route', 'enabled'])

	for item in items:
		if item.route == "/appointment" or item.route == "/my-appointments":
			pass
		else:
			frappe.db.set_value("Portal Menu Item", item.name, "enabled", 0)

	frappe.db.commit()

@frappe.whitelist()
def delete_draft_consultation(doctype, name):
	frappe.delete_doc(doctype, name, ignore_permissions=True, ignore_missing=False)

def get_fiscal_year_data(from_fiscal_year, to_fiscal_year):
	fiscal_year = frappe.db.sql("""select min(year_start_date) as year_start_date,
		max(year_end_date) as year_end_date from `tabMaia Fiscal Year` where
		name between %(from_fiscal_year)s and %(to_fiscal_year)s""",
		{'from_fiscal_year': from_fiscal_year, 'to_fiscal_year': to_fiscal_year}, as_dict=1)

	return fiscal_year[0] if fiscal_year else {}

@frappe.whitelist()
def get_fiscal_year(date=None, fiscal_year=None, label="Date", verbose=1, company=None, as_dict=False):
	return get_fiscal_years(date, fiscal_year, label, verbose, company, as_dict=as_dict)[0]

def get_fiscal_years(transaction_date=None, fiscal_year=None, label="Date", verbose=1, company=None, as_dict=False):
	fiscal_years = frappe.cache().hget("fiscal_years", company) or []

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
				fy.year_start_date desc""".format(cond), {
				"company": company
			}, as_dict=True)

		frappe.cache().hset("fiscal_years", company, fiscal_years)

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