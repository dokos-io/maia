// Copyright (c) 2016, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Codification', {

    codification: function(frm) {
	if(!frm.doc.codification_description)
	    frm.set_value("codification_description", frm.doc.codification);
    }
})

cur_frm.cscript.custom_refresh = function(doc) {
    // use the __islocal value of doc, to check if the doc is saved or not
    if(!doc.__islocal) {
	if(doc.disabled == 1){
	    cur_frm.add_custom_button(__('Enable Code'), function() {
		enable_codification(cur_frm);
	    } );
	}
	else{
	    cur_frm.add_custom_button(__('Disable Code'), function() {
		disable_codification(cur_frm);
	    } );
	}
    }
}

var disable_codification = function(frm){
    var doc = frm.doc;
    frappe.call({
	method: "maia.maia.doctype.codification.codification.disable_enable_codification",
	args: {status: 1, name: doc.name},
	callback: function(r){
	    cur_frm.reload_doc();
	}
    });
}

var enable_codification = function(frm){
    var doc = frm.doc;
    frappe.call({
	method: "maia.maia.doctype.codification.codification.disable_enable_codification",
	args: {status: 0, name: doc.name},
	callback: function(r){
	    cur_frm.reload_doc();
	}
    });
}

frappe.ui.form.on("Codification", "name", function(frm,cdt,cdn){

    frm.doc.change_in_item = 1;

});
frappe.ui.form.on("Codification", "billing_price", function(frm,cdt,cdn){

    frm.doc.change_in_item = 1;

});
frappe.ui.form.on("Codification", "codification_group", function(frm,cdt,cdn){

    frm.doc.change_in_item = 1;

});
frappe.ui.form.on("Codification", "codification_description", function(frm,cdt,cdn){

    frm.doc.change_in_item = 1;

});
