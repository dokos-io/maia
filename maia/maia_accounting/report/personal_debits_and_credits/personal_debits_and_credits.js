// Copyright (c) 2016, DOKOS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Personal Debits and Credits"] = {
	"filters": [
		{
			"fieldname":"practitioner",
			"label": __("Practitioner"),
			"fieldtype": "Link",
			"options": "Professional Information Card",
			"default": frappe.defaults.get_user_default("email"),
			"reqd": 0
		},
		{
			"fieldname":"fiscal_year",
			"label": __("Year"),
			"fieldtype": "Link",
			"options": "Maia Fiscal Year",
			"default": frappe.boot.fiscal_year[0],
			"reqd": 1
		},
		{
			"fieldname":"debit_credit",
			"label": __("Debits or Credits"),
			"fieldtype": "Select",
			"options": "Debits\nCredits",
			"default": "Debits",
			"reqd": 1
		}
	]
};
