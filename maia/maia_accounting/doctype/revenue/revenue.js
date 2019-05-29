// Copyright (c) 2019, DOKOS and contributors
// For license information, please see license.txt

{% include "maia/public/js/controllers/accounting.js" %}

frappe.ui.form.on('Revenue', {
	onload(frm) {
		if(frm.is_new()) {
			set_amount_readonly(frm);
		}

		frm.set_query("party", function() {
			return {
				filters: {
					is_customer: 1
				},
				or_filters: {
					is_social_security: 1
				}
			}
		})
	},
	refresh(frm) {
		check_mandatory_fields(frm);
		set_amount_readonly(frm);
	},

	revenue_type(frm) {
		check_mandatory_fields(frm);
		set_title(frm);
		set_accounting_item(frm)
	},

	patient(frm) {
		set_title(frm);
	},

	party(frm) {
		set_title(frm);
	},

	with_items(frm) {
		set_amount_readonly(frm);
	}
});

frappe.ui.form.on('Revenue Items', {
	codification(frm, cdt, cdn) {
		const item = frappe.get_doc(cdt, cdn);
		frappe.db.get_value("Codification", item.codification, ["billing_price", "codification_description", "accounting_item"], e => {
			item.unit_price = e.billing_price;
			item.description = e.codification_description;
			item.accounting_item = e.accounting_item;
			item.total_amount = flt(item.qty) * flt(e.billing_price);
		})
		.then(() => {
			calculate_total(frm);
			frm.refresh_fields("codifications")
		})
	},

	unit_price(frm, cdt, cdn) {
		const item = frappe.get_doc(cdt, cdn);
		item.total_amount = flt(item.qty) * flt(item.unit_price);
		calculate_total(frm);
		frm.refresh_fields("codifications");
	},

	qty(frm, cdt, cdn) {
		const item = frappe.get_doc(cdt, cdn);
		item.total_amount = flt(item.qty) * flt(item.unit_price);
		calculate_total(frm);
		frm.refresh_fields("codifications");
	},

	codifications_remove(frm) {
		calculate_total(frm);
	}
})

const set_amount_readonly = frm => {
	frm.set_df_property("amount", "read_only", frm.doc.with_items);
	if (!frm.doc.amount) {
		frm.set_value("amount", 0)
	}
}

const calculate_total = frm => {
	let total = 0;
	frm.doc.codifications.forEach(value => {
		total += value.total_amount;
	})
	frm.set_value("amount", total)
}

const check_mandatory_fields = frm => {
	if (frm.doc.revenue_type === "Consultation") {
		frm.set_df_property("party", "reqd", 0);
		frm.set_df_property("patient", "reqd", 1);
	} else if (frm.doc.revenue_type === "Social Security") {
		frm.set_df_property("party", "reqd", 1);
		frm.set_df_property("patient", "reqd", 1);
	} else {
		frm.set_df_property("party", "reqd", 1);
		frm.set_df_property("patient", "reqd", 0);
	}
}

const set_title = frm => {
	if (!frm.doc.label && frm.doc.revenue_type) {
		if (frm.doc.revenue_type == "Consultation" && frm.doc.patient) {
			frm.set_value("label", `${frm.doc.patient}-${__(frm.doc.revenue_type)}`);
		} else if (frm.doc.revenue_type == "Personal credit") {
			frm.set_value("label", `${__(frm.doc.revenue_type)}`);
		} else if (frm.doc.party) {
			frm.set_value("label", `${frm.doc.party}-${__(frm.doc.revenue_type)}`);
		}
	} else {
		frm.set_value("label", "");
	}
}

const set_accounting_item = frm => {
	if (frm.doc.revenue_type == "Personal credit") {
		frappe.db.get_value("Accounting Item", {accounting_item_type: "Practitioner"}, "name", e => {
			frm.set_value("accounting_item", e.name)
		})
	} else {
		frm.set_value("accounting_item", "")
	}
}