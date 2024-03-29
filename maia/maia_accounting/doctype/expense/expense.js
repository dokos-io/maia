// Copyright (c) 2019, DOKOS and contributors
// For license information, please see license.txt

{% include "maia/public/js/controllers/accounting.js" %}

frappe.ui.form.on('Expense', {
	onload(frm) {
		frm.set_query("party", function() {
			return {
				filters: {
					allow_expenses: 1
				},
				or_filters: {
					is_social_contribution: 1,
				}
			}
		})

		frm.set_query("accounting_item", function() {
			return {
				filters: {
					accounting_journal: "Purchases"
				}
			}
		})

		frm.set_df_property("party", "reqd", 1);
	},
	before_save(frm) {
		frm.toggle_reqd("accounting_item", frm.doc.with_items == 1 ? 0 : 1)
		if (frm.doc.with_items == 1 && frm.doc.expense_items) {
			calculate_total(frm);
		}
	},
	refresh(frm) {
		frm.toggle_enable("amount", frm.doc.with_items === 1 ? 0 : 1)
	},
	with_items(frm) {
		frm.toggle_enable("amount", frm.doc.with_items === 1 ? 0 : 1)
	},
	amount(frm) {
		if (frm.doc.expense_type === "Meal expense") {
			calculate_deduction(frm);
		}
	},
	transaction_date(frm) {
		if (frm.doc.expense_type === "Meal expense") {
			calculate_deduction(frm);
		}
	},
	party(frm) {
		if (frm.doc.party && !frm.doc.label) {
			frm.set_value("label", `${frm.doc.party}-${__(frm.doc.expense_type)}`);
		}
	},
	expense_type(frm) {
		frm.set_value("with_items", 0);
		frm.set_value("expense_items", []);
		if (frm.doc.expense_type === "Meal expense") {
			calculate_deduction(frm);
			if (frm.doc.party && !frm.doc.label) {
				frm.set_value("label", `${frm.doc.party}-${__(frm.doc.expense_type)}`);
			}
		} else if (frm.doc.expense_type === "Social contributions") {
			add_social_contibutions_items(frm);
			frm.set_query('party', function(frm) {
				return {
					"filters": {
						"is_social_contribution": 1
					}
				};
			});
			frappe.db.get_value("Party", {is_social_contribution: 1}, "party_name", e => {
				if (e) { frm.set_value("party", e.party_name) };
			})
		} else {
			frm.set_value("label", "");
		}
		frm.toggle_reqd("party", 1)
		frm.toggle_reqd("accounting_item", frm.doc.expense_type === "Meal expense" ? 0 : 1)
		frm.toggle_display("party", 1)
		frm.toggle_display("accounting_item", frm.doc.expense_type === "Meal expense" ? 0 : 1)
		
	}
});

frappe.ui.form.on('Expense Items', {
	total_amount(frm, cdt, cdn) {
		calculate_total(frm);
		frm.refresh_fields("expense_items");
		frm.refresh_fields("amount");
	},

	expense_items_remove(frm) {
		calculate_total(frm);
	}
})

const calculate_total = frm => {
	if (frm.doc.expense_items) {
		let total = 0;
		frm.doc.expense_items.forEach(value => {
			total += value.total_amount;
		})
		frm.set_value("amount", total)
	}
}

const calculate_deduction = frm => {
	if (!(frm.doc.amount && frm.doc.transaction_date)) return;

	frm.set_value("with_items", 1);

	const amount = frm.doc.amount;
	const trans_date = new Date(frm.doc.transaction_date);
	let deductible_amount = 0;
	let exemption_limit = 0;

	frappe.db.get_value("Meal Expense Deduction", {"fiscal_year": trans_date.getFullYear()}, ["deductible_amount", "limit"], e => {
		if (e) {
			deductible_amount = e.deductible_amount;
			exemption_limit = e.limit;
		} else {
			frappe.msgprint(__("The deductible amount and deduction limit for {0} could not be found.<br> Please add them in the Meal Expense Deduction doctype.", [trans_date.getFullYear()]))
		}
	})
	.then(() => {
		const deductible_share = Math.max(Math.min(flt(amount), flt(exemption_limit)) - flt(deductible_amount), 0);
		const non_deductible_share = flt(amount) - flt(deductible_share);
		if (!isNaN(deductible_share) && !isNaN(non_deductible_share)) {
			frm.set_value("expense_items", []);
			[deductible_share, non_deductible_share].forEach((value, i) => {
				const acc_type = (i === 0) ? "Meal": "Practitioner";
				frappe.db.get_value("Accounting Item", {"accounting_item_type": acc_type}, ["name", "description"], e => {
					if (e) {
						frm.add_child('expense_items', {
							label: e.name,
							total_amount: value,
							accounting_item: e.name,
							description: e.description
						});
					} else {
						frappe.msgprint(__("No accounting item with account type {0} could be found", [acc_type]))
					}
				})
				.then(() => frm.refresh())
			})
		}
	})
};

const add_social_contibutions_items = frm => {
	frappe.xcall("frappe.client.get_list", {doctype: "Accounting Item", 
			filters: {"accounting_item_type": ["in", ["Social contributions", "Practitioner"]]}})
	.then(e => { 
		if(e) {
			frm.set_value("with_items", 1);
			e.forEach(value => {
				let row = frappe.model.add_child(frm.doc, "Expense Items", "expense_items");
				row.label = value.name;
				row.total_amount = 0.0;
				row.accounting_item = value.name;
			})
			frm.refresh_fields();
		}
	 })
}