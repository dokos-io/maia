// Copyright (c) 2019, DOKOS and contributors
// For license information, please see license.txt

{% include "maia/public/js/controllers/accounting.js" %}

frappe.ui.form.on('Expense', {
	onload(frm) {
		frm.set_query("party", function() {
			return {
				filters: {
					is_supplier: 1
				}
			}
		})
	},
});
