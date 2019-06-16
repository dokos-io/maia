// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('SMS Reminder', {
	refresh: function(frm) {
		edit_values(frm, false);
		frm.add_custom_button(__('Edit values'), function() {
			edit_values(frm, true);
		});
	}
});

const edit_values = (frm, enable) => {
	console.log(enable)
	if (frm.doc.status != "Sent") {
		const fields = ["sender_name", "send_on", "send_to", "message"]
		fields.forEach(f => {
			frm.toggle_enable(f, enable);
		})
	}
}
