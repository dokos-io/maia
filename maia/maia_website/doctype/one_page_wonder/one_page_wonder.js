// Copyright (c) 2018, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('One Page Wonder', {
	refresh: function(frm) {
		update_buttons(frm);
		update_instructions(frm);
		update_credits(frm);
	}
});

var update_buttons = function(frm) {
	if (!frm.doc.__islocal) {
		frm.add_custom_button(__('Update your Website'), function() {
			update_website(frm);
		})
	}
}

var update_website = function(frm) {
	frappe.call({
		method: "maia.maia_website.doctype.one_page_wonder.one_page_wonder.update_website",
		args: {
		},
		callback: function(data) {
			if (!data.exc) {
				frappe.show_alert({message: __("Website Updated"), indicator: 'green'});
			}
		}
	});
}

var update_instructions = function(frm) {
	frappe.call({
		method: "maia.maia_website.doctype.one_page_wonder.one_page_wonder.update_instructions",
		args: {
		},
		callback: function(data) {
			if (!data.exc && data.message) {
				$('[data-fieldname="template_instructions"]').html($(data.message))
			}
		}
	});
}

var update_credits = function(frm) {
	$("<div>" + __('Template adapted from Startbootstrap\'s') + "<a href='https://startbootstrap.com/template-overviews/one-page-wonder/' target='_blank'> "+ __('One Page Wonder') +"</a></div>").appendTo($('[data-fieldname="template_preview"]'))

}
