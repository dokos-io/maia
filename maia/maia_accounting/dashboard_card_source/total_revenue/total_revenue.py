# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
import maia
from frappe.utils import nowdate, fmt_money, now
from frappe.core.page.dashboard.dashboard import cache_card_source, get_from_date_from_timespan

@frappe.whitelist()
@cache_card_source
def get(card_name, from_date=None, to_date=None):
	card = frappe.get_doc('Dashboard Card', card_name)
	timespan = card.timespan
	currency = maia.get_default_currency()
	fiscal_year = maia.get_default_fiscal_year()

	if frappe.db.exists("Professional Information Card", dict(user=frappe.session.user)):
		practitioner = frappe.db.get_value("Professional Information Card", dict(user=frappe.session.user), "name")
	else:
		return fmt_money(0, 0, currency)

	if timespan != "Preregistered":
		if not to_date:
			to_date = nowdate()
		if not from_date:
			from_date = get_from_date_from_timespan(to_date, timespan)
	else:
		to_date = fiscal_year[2]
		from_date = fiscal_year[1]

	revenue = get_revenue(practitioner, from_date, to_date)

	return fmt_money(revenue or 0, 0, currency)

def get_revenue(practitioner, from_date, to_date):
	revenue = frappe.get_all("Revenue", filters={"transaction_date": ["between", [from_date, to_date]], "docstatus": 1, "practitioner": practitioner}, \
		fields=["SUM(amount) as total"])

	if revenue:
		return revenue[0]["total"]
	else:
		return 0