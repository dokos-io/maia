# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
import maia
from frappe.utils import nowdate, now
from frappe.core.page.dashboard.dashboard import get_from_date_from_timespan

@frappe.whitelist()
def get(card_name, from_date=None, to_date=None):
	if frappe.db.exists("Professional Information Card", dict(user=frappe.session.user)):
		practitioner = frappe.db.get_value("Professional Information Card", dict(user=frappe.session.user), "name")
	else:
		return 0

	reconciliations = get_reconciliations(practitioner)

	return reconciliations or 0

def get_reconciliations(practitioner):
	payments = frappe.get_all("Payment", filters={"status": "Unreconciled"}, fields=["COUNT(name) as total"])

	if payments:
		return payments[0]["total"]
	else:
		return 0