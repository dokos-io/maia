# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
import maia
from frappe.utils import nowdate, fmt_money, now, flt
from frappe.core.page.dashboard.dashboard import get_from_date_from_timespan

@frappe.whitelist()
def get(card_name, from_date=None, to_date=None):
	card = frappe.get_doc('Dashboard Card', card_name)
	timespan = card.timespan
	fiscal_year = maia.get_default_fiscal_year()

	if frappe.db.exists("Professional Information Card", dict(user=frappe.session.user)):
		practitioner = frappe.db.get_value("Professional Information Card", dict(user=frappe.session.user), "name")
	else:
		return "{0} %".format(0)

	if timespan != "Custom":
		if not to_date:
			to_date = nowdate()
		if not from_date:
			from_date = get_from_date_from_timespan(to_date, timespan)
	else:
		to_date = fiscal_year[2]
		from_date = fiscal_year[1]

	result = get_without_codification_percentage(practitioner, from_date, to_date)

	return "{0} %".format(result)

def get_without_codification_percentage(practitioner, from_date, to_date):
	income = get_income(practitioner, from_date, to_date)
	without_codification_income = get_without_codification_income(practitioner, from_date, to_date)

	if flt(income) > 0:
		return round(without_codification_income / income, 2)
	else:
		return 0

def get_income(practitioner, from_date, to_date):
	revenue = frappe.get_all("General Ledger Entry", \
		filters={"posting_date": ["between", [from_date, to_date]], "docstatus": 1, "practitioner": practitioner, \
			"accounting_journal": ["in", ["Sales", "Miscellaneous Operations"]]}, \
		fields=["SUM(credit) - SUM(debit) as total"])

	if revenue:
		return revenue[0]["total"]
	else:
		return 0

def get_without_codification_income(practitioner, from_date, to_date):
	codifications = tuple([x["name"] for x in frappe.get_all("Codification", filters={"basic_price": 0})])

	without_codifications = frappe.db.sql("""
			SELECT SUM(ri.total_amount) as total_amount,
			r.amount, r.outstanding_amount
			FROM `tabRevenue` r
			LEFT JOIN `tabRevenue Items` ri
			ON r.name = ri.parent
			WHERE r.docstatus = 1
			AND r.transaction_date >= '{from_date}'
			AND r.transaction_date <= '{to_date}'
			AND ri.codification in {codifications}
		""".format(
			codifications=codifications,
			from_date=from_date,
			to_date=to_date
			), as_dict=True)

	if without_codifications:
		total = 0
		for item in without_codifications:
			if flt(item.amount) != None and flt(item.amount) != 0:
				total += flt(item.total_amount) * ((flt(item.amount) - flt(item.outstanding_amount)) / flt(item.amount))
		return total
	else:
		return 0