// Copyright (c) 2016, DOKOS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Midwife Replacement Report"] = {
    "filters": [
	{
	    "fieldname":"company",
	    "label": __("Company"),
	    "fieldtype": "Link",
	    "options": "Company",
	    "default": frappe.defaults.get_user_default("Company"),
	    "reqd": 1
	},
	{
	    "fieldname":"practicioner",
	    "label": __("Practicioner"),
	    "fieldtype": "Link",
	    "options": "Professional Information Card",
	    "default": frappe.defaults.get_user_default("email"),
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
    "formatter": function(row, cell, value, columnDef, dataContext, default_formatter) {
	if (columnDef.df.fieldname=="account") {
	    value = dataContext.account_name;

	    columnDef.df.link_onclick =
		"erpnext.financial_statements.open_general_ledger(" + JSON.stringify(dataContext) + ")";
	    columnDef.df.is_tree = true;
	}

	value = default_formatter(row, cell, value, columnDef, dataContext);

	if (!dataContext.parent_account) {
	    var $value = $(value).css("font-weight", "bold");
	    if (dataContext.warn_if_negative && dataContext[columnDef.df.fieldname] < 0) {
		$value.addClass("text-danger");
	    }

	    value = $value.wrap("<p></p>").parent().html();
	}

	return value;
    },
    "open_general_ledger": function(data) {
	if (!data.account) return;
	var project = $.grep(frappe.query_report.filters, function(e){ return e.df.fieldname == 'project'; })

	frappe.route_options = {
	    "account": data.account,
	    "company": frappe.query_report_filters_by_name.company.get_value(),
	    "from_date": data.from_date || data.year_start_date,
	    "to_date": data.to_date || data.year_end_date,
	    "project": (project && project.length > 0) ? project[0].$input.val() : ""
	};
	frappe.set_route("query-report", "General Ledger");
    },
    "tree": true,
    "name_field": "account",
    "parent_field": "parent_account",
    "initial_depth": 3
}
