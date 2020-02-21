import frappe
from frappe.utils import nowdate, get_datetime, get_weekdays, formatdate

RRULE_FREQUENCIES = {
	"RRULE:FREQ=DAILY": "Every Day",
	"RRULE:FREQ=WEEKLY": "Every Week",
	"RRULE:FREQ=MONTHLY": "Every Month",
	"RRULE:FREQ=YEARLY": "Every Year"
}

RRULE_DAYS = {
	"MO": "monday",
	"TU": "tuesday",
	"WE": "wednesday",
	"TH": "thursday",
	"FR": "friday",
	"SA": "saturday",
	"SU": "sunday"
}

FRAMEWORK_FREQUENCIES = {v: '{};'.format(k) for k, v in RRULE_FREQUENCIES.items()}
FRAMEWORK_DAYS = {v: k for k, v in RRULE_DAYS.items()}

def execute():
	frappe.db.set_value("System Settings", "System Settings", "time_format", "HH:mm")

	frappe.reload_doc("maia", "doctype", "maia_settings")
	frappe.reload_doctype("Maia Appointment")
	appointments = frappe.get_all("Maia Appointment", fields=["name", "docstatus", "repeat_this_event", "personal_event"])

	for appointment in appointments:
		if appointment.get("docstatus") == 1:
			frappe.db.set_value("Maia Appointment", appointment.get("name"), "status", "Confirmed")
		elif appointment.get("docstatus") == 2:
			frappe.db.set_value("Maia Appointment", appointment.get("name"), "status", "Cancelled")

		if appointment.personal_event and appointment.repeat_this_event:
			doc = frappe.get_doc("Maia Appointment", appointment.name)
			rrule = get_rrule(doc)
			if rrule:
				frappe.db.set_value("Maia Appointment", appointment.name, "rrule", rrule)

	# Delete unsend notifications
	emails = frappe.get_all("Email Queue", filters={"send_after": [">", nowdate()]})
	for email in emails:
		frappe.delete_doc("Email Queue", email.name)

	# Update maia settings
	settings = frappe.get_doc("Maia Settings", None)
	settings.currency = "EUR"
	settings.save()

	# Meal deduction for 2020
	doc = frappe.get_doc({
		"doctype": "Meal Expense Deduction",
		"fiscal_year": 2020,
		"deductible_amount": 4.90,
		"limit": 19.0
	})
	try:
		doc.insert()
		doc.submit()
	except Exception:
		pass

def get_rrule(doc):
	"""
		Transforms the following object into a RRULE:
		{
			"starts_on",
			"ends_on",
			"all_day",
			"repeat_this_event",
			"repeat_on",
			"repeat_till",
			"sunday",
			"monday",
			"tuesday",
			"wednesday",
			"thursday",
			"friday",
			"saturday"
		}
	"""
	rrule = get_rrule_frequency(doc.get("repeat_on")) or ""
	weekdays = get_weekdays()

	if doc.get("repeat_on") == "Weekly":
		byday = [FRAMEWORK_DAYS.get(day.lower()) for day in weekdays if doc.get(day.lower())]
		rrule += "BYDAY={};".format(",".join(byday))

	elif doc.get("repeat_on") == "Monthly":
		week_number = str(get_week_number(get_datetime(doc.get("starts_on"))))
		week_day = weekdays[get_datetime(doc.get("starts_on")).weekday()].lower()
		rrule += "BYDAY=" + week_number + FRAMEWORK_DAYS.get(week_day) + ";"

	if doc.get("interval"):
		rrule += "INTERVAL={};".format(doc.get("interval"))

	if doc.get("repeat_till"):
		rrule += "UNTIL={}".format(formatdate(doc.get("repeat_till"), "YYYYMMdd"))

	if rrule and rrule.endswith(";"):
		rrule = rrule[:-1]

	return rrule

def get_rrule_frequency(repeat_on):
	"""
		Frequency can be one of the following: YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY, MINUTELY, SECONDLY
	"""
	return FRAMEWORK_FREQUENCIES.get(repeat_on)

def get_week_number(dt):
	"""
		Returns the week number of the month for the specified date.
		https://stackoverflow.com/questions/3806473/python-week-number-of-the-month/16804556
	"""
	from math import ceil
	first_day = dt.replace(day=1)

	dom = dt.day
	adjusted_dom = dom + first_day.weekday()

	return int(ceil(adjusted_dom/7.0))
