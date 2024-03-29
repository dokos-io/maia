// Copyright (c) 2016, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Professional Information Card', {
	refresh: function(frm) {
		if (!frm.is_new()&&!frm.doc.user&&frm.doc.email) {
			frappe.confirm(__("Do you want to create a user for this practitioner ?"), function() {
				frm.call('create_user');
				frappe.show_alert({message: __("User creation in progress"), indicator: 'green'});
			});
		}

		frappe.db.get_value("Google Settings", "Google Settings", "enable", r => {
			if (r&&r.enable==="1") {
				frm.toggle_display('google_calendar_section', true);
			}
		})
	},
	sender_name: function(frm) {
		if (frm.doc.sender_name && !isAlphaNumeric(frm.doc.sender_name)) {
			frm.set_value("sender_name", null);
			frappe.throw(__("Please enter only alphanumeric values"));
		}
	}
});


const isAlphaNumeric = ch => {
	return ch.match(/^[a-z0-9]+$/i) !== null;
}