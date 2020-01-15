// Copyright (c) 2020, Dokos SAS
// License: See license.txt

frappe.ui.form.on('Google Calendar', {
	refresh(frm) {
		frm.trigger('show_hide_user')
    },
    reference_document(frm) {
        frm.trigger('show_hide_user')
    },
    show_hide_user(frm) {
        frm.toggle_display("user", !(frm.doc.reference_document == "Maia Appointment"));
    }
});
