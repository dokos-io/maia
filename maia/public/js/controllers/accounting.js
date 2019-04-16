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
		add_payment_btn(frm);
	}
});

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