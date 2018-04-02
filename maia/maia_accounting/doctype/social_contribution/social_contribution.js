// Copyright (c) 2018, DOKOS and contributors
// For license information, please see license.txt
frappe.provide("maia.socialContribution")

frappe.ui.form.on('Social Contribution', {
	onload: function(frm) {
		frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Company",
					name: frm.doc.company,
				},
				callback: function(r, rt) {
					if (r.message) {
						frm.set_value("social_contribution_deductible_account", r.message.social_contributions_deductible_account);
						frm.set_value("social_contribution_non_deductible_account", r.message.personal_debit_account);
						frm.set_value("supplier", r.message.social_contributions_third_party);
					}
				}
			}),

			frm.set_value("transaction_date", frappe.datetime.get_today());
			frm.set_value("posting_date", frappe.datetime.get_today());
			maia.socialContribution.setup_queries(frm);
			calculate_totals(frm);
	},
	non_deductible_csg: function(frm) {
		calculate_totals(frm);
	},
	deductible_csg: function(frm) {
		calculate_totals(frm);
	},
	crds: function(frm) {
		calculate_totals(frm);
	}

});

frappe.ui.form.on('Social Contribution Item', {
	item_code: function(doc, cdt, cdn) {
		var row = locals[cdt][cdn];
		frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Item",
					name: row.item_code,
				},
				callback: function(r, rt) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, "item_name", r.message.item_name);
						frappe.model.set_value(cdt, cdn, 'description', r.message.description);

						frappe.call({
							method: "maia.maia_accounting.doctype.social_contribution.social_contribution.get_default_expense_account",
							args: {
								company: doc.doc.company,
								item_name: row.item_code,
							},
							callback: function(r, rt) {
								if (r.message) {
									frappe.model.set_value(cdt, cdn, 'expense_account', r.message);
								}
							}
						})
					}
				}
			})
		},
		due_amount: function(doc, cdt, cdn) {
			calculate_totals(doc, cdt, cdn);
		}

});


$.extend(maia.socialContribution, {
	setup_queries: function(frm) {
		frm.fields_dict['items'].grid.get_field("item_code").get_query = function(doc, cdt, cdn) {
			return {
				query: "erpnext.controllers.queries.item_query",
				filters: {'is_purchase_item': 1}
			}
		},
		frm.fields_dict['items'].grid.get_field("expense_account").get_query = function(doc, cdt, cdn) {
			return {
				query: "erpnext.controllers.queries.get_expense_account",
				filters:{'company': frm.doc.company}
			}
		}
	}
});

var calculate_totals = function(doc) {
	var deductible_amount = 0;
	$.each(doc.doc["items"] || [], function(i, item) {
			deductible_amount += flt(item.due_amount);
	});
	doc.set_value('deductible_amount', (deductible_amount + flt(doc.doc.deductible_csg)));
	doc.set_value('non_deductible_amount', (flt(doc.doc.non_deductible_csg) + flt(doc.doc.crds)));
}
