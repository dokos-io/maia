// Copyright (c) 2019, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Miscellaneous Operation', {
	setup(frm) {
		frm.set_query("substitute", function(frm, cdt, cdn) {
			return {
				"filters": {
					"is_substitute": 1
				}
			}
		})
	},
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
	refresh(frm) {
		show_general_ledger(frm);
		frm.page.clear_actions_menu();
		add_reconciliation_btn(frm);
	},
	operation_type(frm) {
		frm.set_value("title", null);
		set_item_queries(frm);
		add_operation_related_items(frm);
	},
	get_cash_payments(frm) {
		frappe.xcall("frappe.client.get_list", {doctype: "Payment Method", filters: {"payment_type": "Cash"}})
		.then(e => {
			return frappe.xcall("frappe.client.get_list", {doctype: "Payment", filters: {"payment_method": ["in", e.map(x => x["name"])],
				"status": "Unreconciled", "payment_type": "Incoming Payment"}, fields: ["name", "party", "paid_amount", "payment_date"]})
		})
		.then(e => {
			frm.doc.payment_items = [];
			e.forEach(value => {
				let row = frappe.model.add_child(frm.doc, "Cash Deposit Payments", "payment_items");
				row.payment = value.name;
				row.party = value.party;
				row.date = value.payment_date;
				row.amount = value.paid_amount;
			})
			frm.refresh_fields();
			calculate_cash_amount(frm)
		})
	},
	practitioner(frm) {
		if (frm.doc.operation_type == "Annual Closing") {
			set_annual_closing(frm)
		}
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
		if (!isNaN(frm.doc.difference)) {
			frappe.model.set_value(cdt, cdn, "amount", flt(frm.doc.difference) > 0
				? Math.abs(frm.doc.difference) * -1 : Math.abs(frm.doc.difference));
		}
	}
})

frappe.ui.form.on('Cash Deposit Payments', {
	payment(frm, cdt, cdn) {
		const child = locals[cdt][cdn];
		frappe.db.get_value("Payment", child.payment, ["party", "payment_date", "paid_amount"], e => {
			if (e) {
				frappe.model.set_value(cdt, cdn, "date", e.payment_date);
				frappe.model.set_value(cdt, cdn, "party", e.party);
				frappe.model.set_value(cdt, cdn, "amount", e.paid_amount);
			}
		})
	},
	amount(frm) {
		calculate_cash_amount(frm)
	},

	payment_items_remove(frm) {
		calculate_cash_amount(frm)
	},

	payment_items_add(frm, cdt, cdn) {
		calculate_cash_amount(frm)
	}
})

function findCashEntry(entry) {
	return entry.accounting_journal == "Cash";
  }

const calculate_cash_amount = frm => {
	let cash = 0;
	frm.doc.payment_items.forEach(row => {
		cash += flt(row.amount);
	})

	const itemIndex = frm.doc.items.findIndex(findCashEntry)
	frappe.model.set_value("Miscellaneous Operation Items", frm.doc.items[itemIndex]["name"], "amount", -flt(cash));
	frm.set_value("payments_total", cash);
}

const calculate_debit_credit = frm => {
	let difference = 0;
	frm.doc.items.forEach(row => {
		difference += flt(row.amount);
	})
	frm.set_value("difference", difference);
}

const set_item_queries = main => {
	main.set_query('accounting_item', 'items', function(frm, cdt, cdn) {
		if (main.doc.operation_type == "Miscellaneous Operation") {
			return {
				"filters": {
					"accounting_journal": ["in", ["Sales", "Purchases", "Miscellaneous Operations"]]
				}
			};
		} else if (main.doc.operation_type == "Internal Transfer") {
			return {
				"filters": {
					"accounting_journal": ["in", ["Bank", "Cash"]]
				}
			};
		} else if (main.doc.operation_type == "Fee Retrocession") {
			return {
				"filters": {
					"accounting_journal": ["in", ["Bank", "Cash", "Miscellaneous Operations"]]
				}
			};
		}
	});

	frappe.xcall("frappe.client.get_list", {doctype: "Payment Method", filters: {"payment_type": "Cash"}})
	.then(e => {
		if (e) {
			main.set_query("payment", "payment_items", function(frm, cdt, cdn) {
				return {
					"filters": {
						"payment_method": ["in", e.map(x => x["name"])],
						"status": "Unreconciled",
						"payment_type": "Incoming Payment"
					}
				}
			})
		}
	})
}

const add_operation_related_items = frm => {
	frm.doc.items = [];
	if (["Internal Transfer", "Fee Retrocession"].includes(frm.doc.operation_type)) {
		frappe.xcall("frappe.client.get_list", {doctype: "Accounting Item", 
			filters: {"accounting_journal": ["in", ["Bank", "Cash"]]}, fields: ["name", "accounting_journal"]})
		.then(e => {
			if(e) {
				add_operation_items(frm, e)
			}
		})
	}
	if (["Personal Credit or Debit", "Cash Deposit"].includes(frm.doc.operation_type)) {
		frappe.xcall("frappe.client.get_list", {doctype: "Accounting Item", 
			filters: {"accounting_item_type": ["in", ["Bank", "Cash", "Practitioner"]]}, fields: ["name", "accounting_journal"]})
		.then(e => {
			if(e) {
				add_operation_items(frm, e)
			}
		})
	}
	if (frm.doc.operation_type == "Fee Retrocession") {
		frappe.xcall("frappe.client.get_list", {doctype: "Accounting Item", 
			filters: {"code_2035": "AC"}, fields: ["name", "accounting_journal"]})
		.then(e => {
			if(e) {
				add_operation_items(frm, e)
			}
		})
	}

	if (frm.doc.operation_type == "Annual Closing") {
		set_annual_closing(frm)
	}
}

const add_operation_items = (frm, e) => {
	e.forEach(value => {
		let row = frappe.model.add_child(frm.doc, "Miscellaneous Operation Items", "items");
		row.accounting_item = value.name;
		row.accounting_journal = value.accounting_journal;
	})
	frm.refresh_fields();
}

const show_general_ledger = (frm) => {
	if(frm.doc.docstatus > 0) {
		frm.add_custom_button(__('Accounting Ledger'), function() {
			frappe.route_options = {
				reference_name: frm.doc.name,
				from_date: frappe.datetime.year_start(),
				to_date: frappe.datetime.year_end(),
				practitioner: frm.doc.practitioner
			};
			frappe.set_route("query-report", "Maia General Ledger");
		}, __("View"));
	}
}

const add_reconciliation_btn = frm => {
	if (frm.doc.docstatus == 1 && frm.doc.operation_type=="Cash Deposit" && frm.doc.payment_items.length) {
		frm.page.add_action_item(__('Update clearance dates'), function() {
			frappe.prompt({
				fieldtype:"Date",
				label:__("Clearance Date"),
				fieldname:"clearance_date",
				reqd:1,
				default: frm.doc.posting_date
			},
			function(data) {
				frappe.xcall('maia.maia_accounting.doctype.miscellaneous_operation.miscellaneous_operation.update_clearance_dates',
				{documents: frm.doc.payment_items, date: data.clearance_date})
				.then(() => {
					frm.reload_doc();
					frappe.show_alert({message:__("Clearance dates updated successfully"), indicator:'green'});
				})
			})
		})
	}
}

const set_annual_closing = frm => {
	if(frm.doc.practitioner) {
		frappe.xcall("maia.maia_accounting.doctype.miscellaneous_operation.miscellaneous_operation.get_closing_date",
		{
			date: frm.doc.posting_date,
			practitioner: frm.doc.practitioner
		})
		.then(e => {
			if(e) {
				frm.set_value("posting_date", e[1])
				frm.set_value("title", __("Annual closing {0}", [e[0]]))
				frm.set_value("items", [])
			}
		})
	}
}