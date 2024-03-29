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
					allow_revenues: 1
				},
				or_filters: {
					is_social_security: 1
				}
			}
		})

		frm.set_query("accounting_item", function() {
			return {
				filters: {
					accounting_journal: "Sales"
				}
			}
		})
	},
	refresh(frm) {
		check_mandatory_fields(frm);
		set_amount_readonly(frm);
		add_lost_btn(frm);
	},

	revenue_type(frm) {
		check_mandatory_fields(frm);
		set_title(frm);
		set_accounting_item(frm)
	},

	patient(frm) {
		if (frm.doc.patient) {
			set_title(frm);
		}
		add_billing_address(frm)
	},

	party(frm) {
		if (frm.doc.party) {
			set_title(frm);
		}
		add_billing_address(frm)
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

	frm.set_df_property("accounting_item", "reqd", !frm.doc.with_items);

}

const set_title = frm => {
	if (!frm.doc.label && frm.doc.revenue_type) {
		if (frm.doc.revenue_type == "Consultation" && frm.doc.patient) {
			frm.set_value("label", `${frm.doc.patient}-${__(frm.doc.revenue_type)}`);
		} else if (frm.doc.party) {
			frm.set_value("label", `${frm.doc.party}-${__(frm.doc.revenue_type)}`);
		}
	} else {
		frm.set_value("label", "");
	}
}

const set_accounting_item = frm => {
	frm.set_value("accounting_item", "")

}

const add_billing_address = frm => {
	let party_type, party;
	if (frm.doc.party) {
		party_type = "Party"
		party = frm.doc.party
	} else if (frm.doc.patient) {
		party_type = "Patient Record"
		party = frm.doc.patient
	}

	if (party!=null) {
		frappe.xcall("maia.maia_accounting.doctype.revenue.revenue.get_billing_address", {party_type: party_type, party: party})
		.then(r => {
			console.log(r)
			if (r) {
				frm.set_value("billing_address", r);
			}
		})
	}
}

const add_lost_btn = frm => {
	if (frm.doc.docstatus == 1 && frm.doc.outstanding_amount != 0) {
		frm.page.add_action_item(__('Set as lost'), function() {
			set_lost(frm);
		})
	} else if (frm.doc.docstatus == 1 && frm.doc.outstanding_amount == 0 && frm.doc.declared_lost != 0) {
		frm.page.add_action_item(__('Cancel loss'), function() {
			revert_lost(frm);
		})
	}
}

const set_lost = frm => {
	frappe.xcall('maia.maia_accounting.doctype.revenue.revenue.set_lost', {dn: frm.docname})
	.then(() => {
		frm.reload_doc();
	})
}

const revert_lost = frm => {
	frappe.xcall('maia.maia_accounting.doctype.revenue.revenue.revert_lost', {dn: frm.docname})
	.then(() => {
		frm.reload_doc();
	})
}