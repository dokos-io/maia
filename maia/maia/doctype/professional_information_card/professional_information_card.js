// Copyright (c) 2016, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Professional Information Card', {
    onload_post_render: function(frm) {
		frm.get_field("substitute_user_creation").$input.addClass("btn-warning");
    },
    
    refresh: function(frm) {
		allow_disallow_replacements(frm)
    },

    substitute_user_creation: function(frm) {
		frm.is_dirty()&&frm.save();

		const d = new frappe.ui.Dialog({
			'title': __('Confirm the creation of a substitute'),
			fields: [
				{ fieldtype:"HTML", options:__("Upon clicking <i>Confirm</i> a new user and a new professional informations card will be created.") },
			],
			primary_action_label: __("Confirm"),
			primary_action: () => {
				frappe.xcall("maia.maia.doctype.professional_information_card.professional_information_card.create_replacement_user",
					{origin: frm.doc.name})
				.then((r) => { 
					frappe.show_alert({message:__("Your substitute {0} has now access to Maia", [r]), indicator:'green'});
					frm.refresh_fields("substitute_practitioner")
				 })
				 .catch(error => {
					frappe.show_alert({message:__("An error has prevented the creation of your substitute. Please contact the support."), indicator:'red'});
				 })
				d.hide();
			}
		});
		d.show();
    }
});

const allow_disallow_replacements = frm => {
	frappe.xcall('frappe.limits.get_usage_info')
	.then(result => {
		let enable_replacement = false;
		if (result&&result["enabled_users"]<result["limits"]["users"]) {
			enable_replacement = true;
		}
		frm.toggle_display('replacement', enable_replacement);
		frm.toggle_display('replacement_instructions_section', !enable_replacement);
	 })
}
