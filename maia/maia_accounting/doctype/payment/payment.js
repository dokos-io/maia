// Copyright (c) 2019, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment', {
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
		set_default_payment_method(frm);
	},
	party(frm) {
		frm.events.get_references(frm);
	},
	payment_type(frm) {
		set_default_payment_method(frm);
		set_default_party_type(frm);
	},
	paid_amount(frm) {
		frm.events.get_references(frm);
	},
	get_references(frm) {
		frm.set_value("payment_references", null);

		frappe.xcall("maia.maia_accounting.doctype.payment.payment.get_outstanding_references", 
		{payment_type: frm.doc.payment_type, party_type: frm.doc.party_type, party: frm.doc.party})
		.then(e => {
			if (e.length) {
				e.forEach(doc => {
					let c = frm.add_child("payment_references");
					c.reference_type = doc.doctype;
					c.reference_name = doc.name;
					c.outstanding_amount = doc.outstanding_amount;
				})
				frm.refresh_fields()
			}
		})
		.then(() => frm.events.allocate_paid_amount(frm))
	},
	allocate_paid_amount(frm) {
		frm.set_value("pending_amount", null);

		let total = 0
		frm.doc.payment_references.forEach(row => {
			if (total + row.outstanding_amount <= frm.doc.paid_amount) {
				row.paid_amount = row.outstanding_amount;
				total += row.outstanding_amount;
			} else {
				row.paid_amount = frm.doc.paid_amount - total;
				total += frm.doc.paid_amount - total;
			}
		})

		if (frm.doc.paid_amount > total) {
			frm.set_value("pending_amount", frm.doc.paid_amount - total);
		}
		frm.refresh_fields();
	}
});

const set_default_payment_method = frm => {
	const field = (frm.doc.payment_type === "Outgoing payment") ? "default_outgoing" : "default_incoming";

	frappe.db.get_value("Payment Method", {[field]: 1}, "name", e => {
		if (e) frm.set_value("payment_method", e.name)
	});
}

const set_default_party_type = frm => {
	const party_type = (frm.doc.payment_type === "Outgoing payment") ? "Party" : "Patient Record";
	frm.set_value("party_type", party_type)
}