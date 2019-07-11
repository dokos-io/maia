# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
import maia
from frappe import _
from frappe.utils import nowdate, getdate, formatdate
from frappe.core.page.dashboard.dashboard import cache_source, get_from_date_from_timespan
from frappe.desk.doctype.dashboard_chart.dashboard_chart import get_period_ending

@frappe.whitelist()
@cache_source
def get(chart_name=None, from_date=None, to_date=None):
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

	dates = get_dates(from_date, to_date)
	consultations = get_consultations(from_date, to_date, practitioner)

	result = build_result(dates, consultations)

	return {
		"labels": [formatdate(r[0].strftime('%Y-%m-%d')) for r in result],
		"datasets": [{
			"name": _("Consultations per week"),
			"values": [r[1] for r in result]
		}]
	}

def get_consultations(from_date, to_date, practitioner):
	result = []
	for consult in maia.get_consultation_types():
		consultations = frappe.get_all(consult, filters={"consultation_date": ["between", [from_date, to_date]], \
			"practitioner": practitioner, "docstatus": 1}, fields=["name", "consultation_date"])

		if consultations:
			result.extend(consultations)

	sorted_result = sorted(result, key=lambda k: k['consultation_date']) 
	return sorted_result

def build_result(dates, consultations):
	result = [[getdate(date), 0.0] for date in dates]

	date_index = 0

	for consultation in consultations:
		while getdate(consultation.consultation_date) > result[date_index][0]:
			date_index += 1

		result[date_index][1] += 1

	return result

def get_dates(from_date, to_date):
	dates = [get_period_ending(from_date, "Weekly")]
	while getdate(dates[-1]) < getdate(to_date):
		date = get_period_ending(getdate(dates[-1]), "Weekly")
		dates.append(date)
	return dates