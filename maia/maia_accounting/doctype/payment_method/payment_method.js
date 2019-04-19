// Copyright (c) 2019, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Method', {
	refresh(frm) {
		if (frm.doc.accounting_item) {
			get_payment_type(frm);
		}
	},
	accounting_item(frm) {
		get_payment_type(frm);
	}
});

const get_payment_type = frm => {
	frappe.db.get_value("Accounting Item", frm.doc.accounting_item, "accounting_journal", e => {
		if (["Bank", "Cash"].includes(e.accounting_journal)) {
			frm.set_value("payment_type", e.accounting_journal);
		}
	})
}