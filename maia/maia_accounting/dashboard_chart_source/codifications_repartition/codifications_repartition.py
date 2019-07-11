# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
import maia
from frappe import _
from frappe.utils import nowdate, getdate
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

	if result:
		return {
			"labels": [x["codification"] for x in result],
			"datasets": [{
				"name": _("Codifications Repartition"),
				"values": [x["qty"] for x in result]
			}]
		}
	else:
		return {}

def get_repartition(from_date, to_date, practitioner):
	codifications = frappe.db.sql("""
		SELECT ri.codification, sum(ri.qty) as qty
		FROM `tabRevenue Items` as ri
		INNER JOIN `tabRevenue` as r
		ON ri.parent = r.name
		WHERE r.practitioner = %s
		AND r.transaction_date BETWEEN '{0}' AND '{1}'
		AND r.docstatus=1
		GROUP BY ri.codification
	""".format(getdate(from_date), getdate(to_date)), (practitioner), as_dict=True)

	return codifications
