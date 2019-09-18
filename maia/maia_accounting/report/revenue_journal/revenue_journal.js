// Copyright (c) 2016, DOKOS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Revenue Journal"] = {
	"filters": [
		{
			"fieldname": "practitioner",
			"label": __("Practitioner"),
			"fieldtype": "Link",
			"options": "Professional Information Card",
			"default": frappe.boot.practitioner,
			"reqd": 1
		},
		{
			"fieldname":"from_date",
			"label": __("From date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.year_start()
		},
		{
			"fieldname":"to_date",
			"label": __("To date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.year_end()
		},
	]
};
