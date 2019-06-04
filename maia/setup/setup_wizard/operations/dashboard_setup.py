# Copyright (c) 2018, DOKOS and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
import re
from frappe import _
from frappe.desk.doctype.desk.desk import WidgetCreator

def setup_cards():
	from frappe.desk.doctype.dashboard_card_source.dashboard_card_source import get_config
	for source in frappe.get_all("Dashboard Card Source"):
		config = get_config(source.name)
		parameters = {}

		color = re.search('color: "(.*)"', config)
		parameters["color"] = color.group(1) if color else None

		icon = re.search('icon: "(.*)"', config)
		parameters["icon"] = icon.group(1) if icon else None

		timespan = re.search('timespan: "(.*)"', config)
		parameters["timespan"] = timespan.group(1) if timespan else None

		try:
			frappe.local.lang = frappe.db.get_value("System Settings", None, "language")
			new_card = frappe.new_doc("Dashboard Card")
			new_card.card_name = _(source.name)
			new_card.source = source.name
			new_card.update(parameters)
			new_card.insert(ignore_permissions=True)
		except Exception:
			print(frappe.get_traceback())

def setup_charts():
	from frappe.desk.doctype.dashboard_chart_source.dashboard_chart_source import get_config
	for source in frappe.get_all("Dashboard Chart Source"):
		config = get_config(source.name)
		parameters = {}

		color = re.search('color: "(.*)"', config)
		parameters["color"] = color.group(1) if color else None

		unit = re.search('unit: "(.*)"', config)
		parameters["unit"] = unit.group(1) if unit else None

		width = re.search('width: "(.*)"', config)
		parameters["width"] = width.group(1) if width else None

		chart_type = re.search('type: "(.*)"', config)
		parameters["type"] = chart_type.group(1) if chart_type else None

		timespan = re.search('timespan: "(.*)"', config)
		parameters["timespan"] = timespan.group(1) if timespan else None
		
		timeseries = re.search('timeseries: "(.*) ', config)
		parameters["timeseries"] = timeseries.group(1) if timeseries else None

		try:
			frappe.local.lang = frappe.db.get_value("System Settings", None, "language")
			new_chart = frappe.new_doc("Dashboard Chart")
			new_chart.chart_name = _(source.name)
			new_chart.chart_type = "Preregistered"
			new_chart.filters_json = "{}"
			new_chart.source = source.name
			new_chart.update(parameters)
			new_chart.insert(ignore_permissions=True)
		except Exception:
			print(frappe.get_traceback())

def init_dashboard(user=None):
	if not user:
		users = frappe.get_all("User", filters={"user_type": "System User"})
		for user in users:
			_init_dashboard(user.name)
	else:
		_init_dashboard(user)

def _init_dashboard(user):
	for card in frappe.get_all("Dashboard Card"):
		widget = WidgetCreator("Desk", user=user)
		widget.add_widget("Dashboard Stats", **{
			"card": card.name
		})

	for chart in frappe.get_all("Dashboard Chart"):
		widget = WidgetCreator("Desk", user=user)
		widget.add_widget("Dashboard Chart", **{
			"chart": chart.name
		})

	widget = WidgetCreator("Desk", user=user)
	widget.add_widget("Dashboard Calendar", **{
		"reference": "Maia Appointment",
		"user": user
	})
