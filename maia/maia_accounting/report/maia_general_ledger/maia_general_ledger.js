// Copyright (c) 2016, DOKOS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Maia General Ledger"] = {
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
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"accounting_journal",
			"label": __("Accounting Journal"),
			"fieldtype": "Select",
			"options": ["", "Bank", "Cash", "Miscellaneous operations", "Purchases", "Sales"]
		},
		{
			"fieldname":"accounting_item",
			"label": __("Accounting Item"),
			"fieldtype": "Link",
			"options": "Accounting Item"
		},
		{
			"fieldname":"reference_name",
			"label": __("Reference Document"),
			"fieldtype": "Data"
		},
		{
			"fieldname":"link_docname",
			"label": __("Posting Document"),
			"fieldtype": "Data"
		}
	]
}
