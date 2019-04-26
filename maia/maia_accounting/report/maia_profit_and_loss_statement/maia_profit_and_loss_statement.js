// Copyright (c) 2016, DOKOS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Maia Profit and Loss Statement"] = {
	"filters": [
		{
			"fieldname": "practitioner",
			"label": __("Practitioner"),
			"fieldtype": "Link",
			"options": "Professional Information Card",
			"reqd": 1
		},
		{
			"fieldname":"from_fiscal_year",
			"label": __("Period Start"),
			"fieldtype": "Link",
			"options": "Maia Fiscal Year",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("fiscal_year")
		},
		{
			"fieldname":"to_fiscal_year",
			"label": __("Period End"),
			"fieldtype": "Link",
			"options": "Maia Fiscal Year",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("fiscal_year")
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
			"default": "Yearly",
			"reqd": 1
		}
	],
	formatter: function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (!data.parent_account) {
			value = $(`<span>${value}</span>`);

			let $value = $(value).css("font-weight", "bold");
			if (data.warn_if_negative && data[column.fieldname] < 0) {
				$value.addClass("text-danger");
			}

			value = $value.wrap("<p></p>").parent().html();
		}
		return value;
	}
}
