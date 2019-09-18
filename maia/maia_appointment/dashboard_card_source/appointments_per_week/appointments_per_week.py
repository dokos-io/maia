# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import nowdate
from maia.utilities import difference_in_weeks
from frappe.core.page.dashboard.dashboard import get_from_date_from_timespan

from maia.maia_appointment.doctype.maia_appointment.maia_appointment import get_events

@frappe.whitelist()
def get(card_name, from_date=None, to_date=None):
	card = frappe.get_doc('Dashboard Card', card_name)
	timespan = card.timespan

	if not to_date:
		to_date = nowdate()
	if not from_date:
		from_date = get_from_date_from_timespan(to_date, timespan)

	events = get_events(from_date, to_date, frappe.session.user)

	weeks_diff = difference_in_weeks(from_date, to_date)

	return round(len(events) / weeks_diff)