// Copyright (c) 2016, DOKOS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Trial Balance"] = {
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
			"label": __("Period Start"),
			"fieldtype": "Date",
			"default": frappe.datetime.year_start(),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"to_date",
			"label": __("Period End"),
			"fieldtype": "Date",
			"default": frappe.datetime.year_end(),
			"reqd": 1,
			"width": "60px"
		}
	],
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (data.bold) {
			var $value = $(value).css("font-weight", "bold");
			value = $value.wrap("<p></p>").parent().html();
		}

		return value;
	},
};
