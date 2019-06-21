// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and Contributors
// See license.txt

// render
frappe.listview_settings['Expense'] = {
	get_indicator: function(doc) {
		if (["Paid", "Unpaid"].includes(doc.status)) {
			return [__(doc.status), doc.status === "Paid" ? "green" : "orange"];
		}
	},
	onload: function(listview) {
		listview.page.add_action_item( __('Payment'), function() {
			const method = 'maia.maia_accounting.doctype.payment.payment.get_list_payment'
			frappe.xcall(method, {names: listview.get_checked_items(true), dt: "Expense"})
			.then(e => {
				const doclist = frappe.model.sync(e);
				frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
			})
		})
	}
};