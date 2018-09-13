// Copyright (c) 2018, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bank Reconciliation', {
	onload: function(frm) {
		frm.add_custom_button(__('Add patient records to payment entries'), () => {
			let promises = [];
			$.each(frm.doc.payment_entries || [], function(i, value) {
				let p = new Promise(resolve => {
					frappe.db.get_value(value.payment_document, value.payment_entry, 'patient_record', (r) => {
						if(r.patient_record) value.patient_record = r.patient_record;
						resolve();
					})
				});
				promises.push(p);
			})
	
			Promise.all(promises).then(() => {
				frm.refresh_field('payment_entries');
			})
		})
	}
})