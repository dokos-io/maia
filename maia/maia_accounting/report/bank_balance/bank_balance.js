// Copyright (c) 2016, DOKOS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Bank Balance"] = {
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
	onload: function(report) {
		report.page.add_action_item(__('Update a bank balance'), function() {
			update_bank_balance(report);
		})

		report.page.add_inner_message(__("Don't forget to add the initial and final bank statement values for your bank accounts through the action button"))
	},
	after_datatable_render: function(dt) {
		dt.rowmanager.collapseAllNodes();
	}
}

const update_bank_balance = (report) => {
	const start = report.filters.filter(f => f.fieldname == "from_date")
	const end = report.filters.filter(f => f.fieldname == "to_date")
	let start_date = frappe.datetime.year_start();
	let end_date = frappe.datetime.year_end();

	if (start.length) { start_date = start[0].value }
	if (end.length) { end_date = end[0].value }

	const d = new frappe.ui.Dialog({
		title: __('Bank balance'),
		fields: [
			{
				label: __("Bank Account"),
				fieldname: "bank_account",
				fieldtype: "Link",
				options: "Maia Bank Account",
				reqd: 1,
				onchange: function() {
					frappe.xcall('maia.maia_accounting.report.bank_balance.bank_balance.get_bank_balance',
					{from_date: start_date, to_date: end_date, bank_account: d.fields_dict.bank_account.get_value()})
					.then(r => {
						d.fields_dict.start_balance.set_input(r["start"]);
						d.fields_dict.end_balance.set_input(r["end"]);
					})
				}
			},
			{
				fieldname: "balance_section",
				fieldtype: "Section Break"
			},
			{
				label: __("Period Start Date"),
				fieldname: "start_date",
				fieldtype: "Date",
				default: start_date
			},
			{
				label: __("Period Start Balance"),
				fieldname: "start_balance",
				fieldtype: "Currency"
			},
			{
				fieldname: "end_column",
				fieldtype: "Column Break"
			},
			{
				label: __("Period End Date"),
				fieldname: "end_date",
				fieldtype: "Date",
				default: end_date
			},
			{
				label: __("Period End Balance"),
				fieldname: "end_balance",
				fieldtype: "Currency"
			}
		],
		primary_action: function() {
			const data = d.get_values();

			frappe.xcall('maia.maia_accounting.doctype.bank_statement_balance.bank_statement_balance.update_balance', data)
			.then(e => {
				report.refresh();
				d.hide();
				frappe.show_alert({message:__("Bank balances updated successfully"), indicator:'green'});
			 })
			
		},
		primary_action_label: __('Update')
	});
	d.show();
}