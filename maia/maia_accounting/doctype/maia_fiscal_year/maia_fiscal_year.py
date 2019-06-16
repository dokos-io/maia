# -*- coding: utf-8 -*-
# Copyright (c) 2019, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from frappe.utils import getdate, add_days, add_years, cstr
from dateutil.relativedelta import relativedelta

from frappe.model.document import Document

class FiscalYearIncorrectDate(frappe.ValidationError): pass

class MaiaFiscalYear(Document):
	def validate(self):
		self.validate_dates()

		if not self.is_new():
			year_start_end_dates = frappe.db.sql("""select year_start_date, year_end_date
				from `tabMaia Fiscal Year` where name=%s""", (self.name))

			if year_start_end_dates:
				if getdate(self.year_start_date) != year_start_end_dates[0][0] or getdate(self.year_end_date) != year_start_end_dates[0][1]:
					frappe.throw(_("Cannot change Fiscal Year Start Date and Fiscal Year End Date once the Fiscal Year is saved."))

	def validate_dates(self):
		if getdate(self.year_start_date) > getdate(self.year_end_date):
			frappe.throw(_("Fiscal Year Start Date should be one year earlier than Fiscal Year End Date"),
				FiscalYearIncorrectDate)

		date = getdate(self.year_start_date) + relativedelta(years=1) - relativedelta(days=1)

		if getdate(self.year_end_date) != date:
			frappe.throw(_("Fiscal Year End Date should be one year after Fiscal Year Start Date"),
				FiscalYearIncorrectDate)

	def on_update(self):
		check_duplicate_fiscal_year(self)
		frappe.cache().delete_value("fiscal_years")
	
	def on_trash(self):
		frappe.cache().delete_value("fiscal_years")

@frappe.whitelist()
def check_duplicate_fiscal_year(doc):
	year_start_end_dates = frappe.db.sql("""select name, year_start_date, year_end_date from `tabMaia Fiscal Year` where name!=%s""", (doc.name))
	for fiscal_year, ysd, yed in year_start_end_dates:
		if (getdate(doc.year_start_date) == ysd and getdate(doc.year_end_date) == yed) and (not frappe.flags.in_test):
					frappe.throw(_("Fiscal Year Start Date and Fiscal Year End Date are already set in Fiscal Year {0}").format(fiscal_year))


@frappe.whitelist()
def auto_create_fiscal_year():
	for d in frappe.db.sql("""select name from `tabMaia Fiscal Year` where year_end_date = date_add(current_date, interval 3 day)"""):
		try:
			current_fy = frappe.get_doc("Fiscal Year", d[0])

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

def get_from_and_to_date(fiscal_year):
	from_and_to_date_tuple = frappe.db.sql("""select year_start_date, year_end_date
		from `tabFiscal Year` where name=%s""", (fiscal_year))[0]

	from_and_to_date = {
		"from_date": from_and_to_date_tuple[0],
		"to_date": from_and_to_date_tuple[1]
	}

	return from_and_to_date
