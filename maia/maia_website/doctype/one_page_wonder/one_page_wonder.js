// Copyright (c) 2018, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('One Page Wonder', {
	refresh: function(frm) {
		update_instructions(frm);
		update_credits(frm);
	}
});

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
	$("<div>" + __('Adapté du modèle Startbootstrap') + "<a href='https://blackrockdigital.github.io/startbootstrap-one-page-wonder/' target='_blank'> "+ __('One Page Wonder') +"</a></div>").appendTo($('[data-fieldname="template_preview"]'))

}
