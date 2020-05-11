// Copyright (c) 2019, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on(this.frm.doctype, {
	onload(frm) {
		if (frm.is_new()) {
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
						frm.set_value("practitioner", data.message.name);
					}
				}
			})
		}
	},
	refresh(frm) {
		frm.page.clear_actions_menu();
		add_payment_btn(frm);
		show_general_ledger(frm);
	}
});

const show_general_ledger = (frm) => {
	if(frm.doc.docstatus > 0) {
		frm.add_custom_button(__('Accounting Ledger'), function() {
			frappe.route_options = {
				reference_name: frm.doc.name,
				from_date: frm.doc.posting_date,
				to_date: frm.doc.posting_date,
				practitioner: frm.doc.practitioner
			};
			frappe.set_route("query-report", "Maia General Ledger");
		}, __("View"));
	}
}

const add_payment_btn = frm => {
	if (frm.doc.docstatus == 1 && frm.doc.outstanding_amount != 0) {
		frm.page.add_action_item(__('Payment'), function() {
			make_payment(frm);
		})
	}
}

const make_payment = frm => {
	frappe.xcall('maia.maia_accounting.doctype.payment.payment.get_payment', {dt: frm.doctype, dn: frm.docname})
	.then(e => {
		if (e) {
			const doclist = frappe.model.sync(e);
			frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
		}
	})
}