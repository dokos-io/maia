import frappe
import math
from frappe.utils import getdate, cint

def difference_in_weeks(start_date, end_date):
	dt_diff = getdate(end_date) - getdate(start_date)
	dt_diff_seconds = dt_diff.days * 86400.0 + dt_diff.seconds
	dt_diff_days = math.floor(dt_diff_seconds / 86400.0)
	weeks_diff = cint(math.ceil(dt_diff_days / 7.0))

	return weeks_diff