# Copyright (c) 2013, DOKOS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from collections import defaultdict

def execute(filters=None):

	data = get_data(filters)
	columns = get_columns()

	return columns, data

def get_data(filters=None):

	revenue = frappe.db.sql("""
		SELECT r.name as revenue_name, r.amount as revenue_amount,
		r.transaction_date, r.patient, r.party, r.consultation_type,
		r.consultation, pr.parent as payment, pr.paid_amount as paid_amount,
		pay.payment_method
		FROM tabRevenue r
		LEFT JOIN `tabPayment References` pr
		ON pr.reference_name = r.name
		LEFT JOIN `tabPayment` pay
		ON pay.name = pr.parent
		WHERE r.practitioner="{practitioner}"
		AND r.transaction_date >= "{from_date}"
		AND r.transaction_date <= "{to_date}"
	""".format(
		practitioner=filters.practitioner,
		from_date=filters.from_date,
		to_date=filters.to_date
	), as_dict=True)

	docs = defaultdict(float)

	for rev in revenue:
		rev["consultation_type"] = _(rev["consultation_type"])
		docs[rev["revenue_name"]] += float(rev["paid_amount"] or 0)
		rev["paid"] = _("Yes") if docs[rev["revenue_name"]] == rev["revenue_amount"] else _("No")

	return revenue

def get_columns():
	return [
		{
		"fieldname": "revenue_name",
		"label": _("Revenue"),
		"fieldtype": "Link",
		"options": "Revenue",
		"width": 200
		},
		{
		"fieldname": "transaction_date",
		"label": _("Transaction date"),
		"fieldtype": "Date",
		"width": 150
		},
		{
		"fieldname": "patient",
		"label": _("Patient"),
		"fieldtype": "Data",
		"width": 300
		},
		{
		"fieldname": "party",
		"label": _("Party"),
		"fieldtype": "Data",
		"width": 150
		},
		{
		"fieldname": "revenue_amount",
		"label": _("Revenue amount"),
		"fieldtype": "Currency",
		"width": 180
		},
		{
		"fieldname": "paid_amount",
		"label": _("Paid amount"),
		"fieldtype": "Currency",
		"width": 180
		},
		{
		"fieldname": "paid",
		"label": _("Is totally paid ?"),
		"fieldtype": "Data",
		"width": 120
		},
		{
		"fieldname": "payment",
		"label": _("Payment document"),
		"fieldtype": "Link",
		"options": "Payment",
		"width": 250
		},
		{
		"fieldname": "payment_method",
		"label": _("Payment method"),
		"fieldtype": "Data",
		"width": 250
		},
		{
		"fieldname": "consultation_type",
		"label": _("Consultation Type"),
		"fieldtype": "Data",
		"width": 300
		},
		{
		"fieldname": "consultation",
		"label": _("Consultation"),
		"fieldtype": "Data",
		"width": 300
		}
	]
