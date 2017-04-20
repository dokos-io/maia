// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt
frappe.provide("maia");

frappe.ui.form.on('Pregnancy', {
	refresh: function(frm) {

	}
});

maia.PregnancyController = frappe.ui.form.Controller.extend({
    set_default_print_format: function() {
	this.frm.meta.default_print_format = "Pregnancy Folder";
    }
});

$.extend(this.frm.cscript, new maia.PregnancyController({frm: this.frm}));
