// Copyright (c) 2019, DOKOS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Declaration 2035"] = {
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
			"fieldname": "fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Maia Fiscal Year",
			"default": frappe.boot.fiscal_year[0],
			"reqd": 1
		}
	],
	get_datatable_options(options) {
		return Object.assign(options, {
			serialNoColumn: false
		});
	}
}
