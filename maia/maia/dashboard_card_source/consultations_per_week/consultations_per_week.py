# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
import maia
from frappe.utils import nowdate
from maia.utilities import difference_in_weeks
from frappe.core.page.dashboard.dashboard import get_from_date_from_timespan

@frappe.whitelist()
def get(card_name, from_date=None, to_date=None):
	card = frappe.get_doc('Dashboard Card', card_name)
	timespan = card.timespan

	if frappe.db.exists("Professional Information Card", dict(user=frappe.session.user)):
		practitioner = frappe.db.get_value("Professional Information Card", dict(user=frappe.session.user), "name")
	else:
		return 0

	if not to_date:
		to_date = nowdate()
	if not from_date:
		from_date = get_from_date_from_timespan(to_date, timespan)

	consults = get_consultations(practitioner, from_date, to_date)

	weeks_diff = difference_in_weeks(from_date, to_date)

	return round(consults / weeks_diff)

def get_consultations(practitioner, from_date, to_date):
	doctypes = maia.get_consultation_types()

	result = 0
	for dt in doctypes:
		consultations = frappe.get_all(dt, filters={"consultation_date": ["between", [from_date, to_date]], "docstatus": 1, "practitioner": practitioner})
		if consultations:
			result += len(consultations)

	return result