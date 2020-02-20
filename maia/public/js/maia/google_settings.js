frappe.ui.form.on('Google Settings', {
    refresh(frm) {
        frm.dashboard.clear_headline()
        frm.dashboard.set_headline(__("Please contact the support to activate your google calendar access"));
    }
})