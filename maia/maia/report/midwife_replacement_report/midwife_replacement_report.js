// Copyright (c) 2016, DOKOS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Midwife Replacement Report"] = {
	"filters": [
		{
			"fieldname":"practitioner",
			"label": __("Practitioner"),
			"fieldtype": "Link",
			"options": "Professional Information Card",
			"default": frappe.boot.practitioner,
			"reqd": 0
		},
		{
			"fieldname":"from_fiscal_year",
			"label": __("Start Year"),
			"fieldtype": "Link",
			"options": "Maia Fiscal Year",
			"default": frappe.defaults.get_user_default("fiscal_year"),
			"reqd": 1
		},
		{
			"fieldname":"to_fiscal_year",
			"label": __("End Year"),
			"fieldtype": "Link",
			"options": "Maia Fiscal Year",
			"default": frappe.defaults.get_user_default("fiscal_year"),
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
	],
	formatter: function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (data.account_name == "substitute") {
			value = $(`<span>${value}</span>`);

			let $value = $(value).css("font-weight", "bold");
			value = $value.wrap("<p></p>").parent().html();
		} else if (data.account_name == "dates") {
			value = $(`<span>${value}</span>`);

			let $value = $(value).css("font-style", "italic");
			value = $value.wrap("<p></p>").parent().html();
		}
		return value;
	},
	get_datatable_options: function (options) {
		console.log(options)
		return Object.assign(options, {
			tooltipOptions: {
				formatTooltipX: d => (d + '').toUpperCase(),
				formatTooltipY: d => d + ' ' + frappe.defaults.get_user_default("currency"),
			}
		});
	}
}
