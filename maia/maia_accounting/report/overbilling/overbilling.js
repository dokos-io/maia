// Copyright (c) 2019, DOKOS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Overbilling"] = {
	"filters": [
		{
			"fieldname":"practitioner",
			"label": __("Practitioner"),
			"fieldtype": "Link",
			"options": "Professional Information Card",
			"default": frappe.boot.practitioner,
			"reqd": 1
		},
		{
			"fieldname":"from_fiscal_year",
			"label": __("Start Year"),
			"fieldtype": "Link",
			"options": "Maia Fiscal Year",
			"default": frappe.boot.fiscal_year[0],
			"reqd": 1
		},
		{
			"fieldname":"to_fiscal_year",
			"label": __("End Year"),
			"fieldtype": "Link",
			"options": "Maia Fiscal Year",
			"default": frappe.boot.fiscal_year[0],
			"reqd": 1
		},
		{
			"fieldname": "periodicity",
			"label": __("Periodicity"),
			"fieldtype": "Select",
			"options": [
			{ "value": "Monthly", "label": __("Monthly") },
			{ "value": "Quarterly", "label": __("Quarterly") },
			{ "value": "Half-Yearly", "label": __("Half-Yearly") },
			{ "value": "Yearly", "label": __("Yearly") }
			],
			"default": "Monthly",
			"reqd": 1
		}
	]
}

