# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
import maia
from frappe.utils import nowdate, fmt_money, now
from maia.utilities import difference_in_weeks
from frappe.core.page.dashboard.dashboard import cache_card_source, get_from_date_from_timespan

@frappe.whitelist()
@cache_card_source
def get(card_name, from_date=None, to_date=None):
	card = frappe.get_doc('Dashboard Card', card_name)
	timespan = card.timespan

	if frappe.db.exists("Professional Information Card", dict(user=frappe.session.user)):
		practitioner = frappe.get_doc("Professional Information Card", dict(user=frappe.session.user))
	else:
		return 0

	if not to_date:
		to_date = nowdate()
	if not from_date:
		from_date = get_from_date_from_timespan(to_date, timespan)

	patients = get_new_patients(practitioner, from_date, to_date)

	return patients

def get_new_patients(practitioner, from_date, to_date):
	patients = frappe.get_all("Patient Record", filters={"creation": ["between", [from_date, to_date]]}, fields=["COUNT(name) as total"])

	if patients:
		return patients[0]["total"]
	else:
		return 0