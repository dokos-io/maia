# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
import maia
from frappe import _
from frappe.utils import nowdate
from frappe.core.page.dashboard.dashboard import cache_source, get_from_date_from_timespan

@frappe.whitelist()
@cache_source
def get(chart_name=None, from_date = None, to_date = None):
	chart = frappe.get_doc('Dashboard Chart', chart_name)
	timespan = chart.timespan

	if not to_date:
		to_date = nowdate()
	if not from_date:
		from_date = get_from_date_from_timespan(to_date, timespan)

	if frappe.db.exists("Professional Information Card", dict(user=frappe.session.user)):
		practitioner = frappe.db.get_value("Professional Information Card", dict(user=frappe.session.user), "name")
	else:
		practitioner = None

	result = get_repartition(from_date, to_date, practitioner)
	labels = [_(x) for x in maia.get_consultation_types()]

	return {
		"labels": labels,
		"datasets": [{
			"name": _("Consultation Repartition"),
			"values": result
		}]
	}

def get_repartition(from_date, to_date, practitioner):
	result = []
	for consult in maia.get_consultation_types():
		consult_count = frappe.get_all(consult, filters={"consultation_date": ["between", [from_date, to_date]], \
			"practitioner": practitioner, "docstatus": 1}, fields=["COUNT(name) as total"])
		
		if consult_count:
			result.append(consult_count[0]["total"])
		else:
			result.append(0)
	
	return result
