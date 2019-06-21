// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and Contributors
// See license.txt

// render
frappe.listview_settings['Payment'] = {
	get_indicator: function(doc) {
		if (["Unreconciled", "Reconciled"].includes(doc.status)) {
			return [__(doc.status), doc.status === "Reconciled" ? "green" : "orange"];
		}
	},
	onload: function(listview) {
		listview.page.add_action_item( __('Update clearance date'), function() {
			const method = 'maia.maia_accounting.doctype.payment.payment.update_clearance_dates'
			frappe.prompt({
				fieldtype:"Date",
				label:__("Clearance Date"),
				fieldname:"clearance_date",
				reqd:1,
				default: frappe.datetime.nowdate()
			},function(data) {
				listview.call_for_selected_items(method, {date: data.clearance_date})
			})
		})
	}
};