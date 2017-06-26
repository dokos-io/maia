// Copyright (c) 2016, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Professional Information Card', {
    onload_post_render: function(frm) {
	frm.get_field("substitute_user_creation").$input.addClass("btn-warning");
    },
    
    refresh: function(frm) {

    },

    substitute_user_creation: function(frm) {
	var d = new frappe.ui.Dialog({
	    'title': __('Create a New Substitute User ?'),
	    fields: [
		{ fieldtype:"HTML", options:__("Are you certain you want to create a new substitute user ?") },
		{ fieldname: 'ok_button', fieldtype: 'Button', label: __("Yes") },
	    ]
	});
	d.show();
	d.fields_dict.ok_button.input.onclick = function () {
		return frappe.call({
		    method: "maia.maia.doctype.professional_information_card.professional_information_card.replacement_user",
		    args: {
			contact: frm.doc.name
		    },
	    callback: function(r) {
		frm.set_value("substitute_user", r.message);
		d.hide();
	    }
		});
	};
    }
});
