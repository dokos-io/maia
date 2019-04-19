// Copyright (c) 2019, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Miscellaneous Operation', {
	onload(frm) {
		frappe.call({
			"method": "maia.client.get_practitioner",
			args: {
				doctype: "Professional Information Card",
				filters: {
					user: frappe.session.user
				},
				fieldname: "name"
			},
			cache: false,
			callback: function(data) {
				if (!data.exe && data.message) {
					frappe.model.set_value(frm.doctype, frm.docname, "practitioner", data.message.name)
				}
			}
		})

		set_item_queries(frm);
	},
	operation_type(frm) {
		set_item_queries(frm);
		add_operation_related_items(frm);
	}
});

frappe.ui.form.on('Miscellaneous Operation Items', {
	accounting_item(frm, cdt, cdn) {
		const child = locals[cdt][cdn];
		frappe.db.get_value("Accounting Item", child.accounting_item, "accounting_journal", e => {
			if (e) frappe.model.set_value(cdt, cdn, "accounting_journal", e.accounting_journal);
		})
	},
	amount(frm) {
		calculate_debit_credit(frm);
	},

	items_remove(frm) {
		calculate_debit_credit(frm);
	},

	items_add(frm, cdt, cdn) {
		frappe.model.set_value(cdt, cdn, "amount", flt(frm.doc.difference) > 0 ? Math.abs(frm.doc.difference) * -1 : Math.abs(frm.doc.difference));
	}
})

const calculate_debit_credit = frm => {
	let difference = 0;
	frm.doc.items.forEach(row => {
		difference += flt(row.amount);
	})
	frm.set_value("difference", difference);
}

const set_item_queries = frm => {
	if (frm.doc.operation_type == "Miscellaneous Operation") {
		frm.set_query('accounting_item', 'items', function(frm, cdt, cdn) {
			return {
				"filters": {
					"accounting_journal": ["in", ["Sales", "Purchases", "Miscellaneous Operations"]]
				}
			};
		});
	} else if (frm.doc.operation_type == "Internal Transfer") {
		frm.set_query('accounting_item', 'items', function(frm, cdt, cdn) {
			return {
				"filters": {
					"accounting_journal": ["in", ["Bank", "Cash"]]
				}
			};
		});
	}
}

const add_operation_related_items = frm => {
	if (frm.doc.operation_type == ["Internal Transfer", "Opening Entry"]) {
		frappe.xcall("frappe.client.get_list", {doctype: "Accounting Item", 
			filters: {"accounting_journal": ["in", ["Bank", "Cash"]]}, fields: ["name", "accounting_journal"]})
		.then(e => {
			if(e) {
				frm.doc.items = [];
				e.forEach(value => {
					let row = frappe.model.add_child(frm.doc, "Miscellaneous Operation Items", "items");
					row.accounting_item = value.name;
					row.accounting_journal = value.accounting_journal;
				})
				frm.refresh_fields();
			}
		})
	}
}