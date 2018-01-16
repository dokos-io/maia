// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Meal Expense', {
	onload: function(frm) {
		frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Company",
					name: frm.doc.company,
				},
				callback: function(r, rt) {
					if (r.message) {
						frm.set_value("meal_expense_deductible_account", r.message.meal_expense_deductible_account);
						frm.set_value("meal_expense_non_deductible_account", r.message.meal_expense_non_deductible_account);
					}
				}
			}),

			frm.set_value("transaction_date", frappe.datetime.get_today())
			frm.set_value("posting_date", frappe.datetime.get_today())
	},
	refresh: function(frm) {
	},
	meal_amount: function(frm) {
		calculate_deduction(frm);
	},
	transaction_date: function(frm) {
		calculate_deduction(frm);
	}
});

var calculate_deduction = function(frm) {
	var amount = frm.doc.meal_amount;
	var trans_date = new Date(frm.doc.transaction_date)
	if (new Date("2017-01-01") <= trans_date && trans_date <= new Date("2017-12-31")) {
		var benefit_in_kind = 4.75;
		var exemption_limit = 18.40;
	} else if (new Date("2018-01-01") <= trans_date && trans_date <= new Date("2018-12-31")) {
		var benefit_in_kind = 4.80;
		var exemption_limit = 18.60;
	} else {
		frappe.msgprint(__("This tool calculates meal expenses for 2017 and 2018 only"))
	};

	var deductible_share = Math.max(Math.min(amount, exemption_limit) - benefit_in_kind, 0);
	var non_deductible_share = amount - deductible_share;
	if (!isNaN(deductible_share) && !isNaN(non_deductible_share)) {
		frm.set_value("deductible_share", deductible_share);
		frm.set_value("non_deductible_share", non_deductible_share);
	}
};
