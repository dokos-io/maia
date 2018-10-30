// Copyright (c) 2018, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Entry', {
	refresh: function(frm) {
		if (frm.doc.references && frm.doc.payment_type==="Receive") {
			let patient_records = [];
			let promises = [];
			frm.doc.references.forEach(value => {
				let p = new Promise(resolve => {
					frappe.db.get_value(value.reference_doctype, value.reference_name, 'patient_record', (r) => {
						patient_records.push(r.patient_record);
						resolve();
					})
				});
				promises.push(p);
			})

			Promise.all(promises).then(() => {
				console.log(patient_records);
				let patient_record = [ ...new Set(patient_records) ]
				if (patient_record.length == 1) {
					frm.set_value("patient_record", patient_record[0])
				}
			})
		}
	}
})