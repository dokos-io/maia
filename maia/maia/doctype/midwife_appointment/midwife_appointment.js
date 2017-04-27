// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Midwife Appointment', {
    onload: function(frm) {
	frappe.call({
	    "method": "maia.client.get_practitioner",
	    args: {
		doctype: "Professional Information Card",
		filters: {user: user},
		fieldname: "name"
	    },
	    cache: false,
	    callback: function (data) {
		console.log(data);
		if (!data.exe && data.message) {
		    frappe.model.set_value(frm.doctype, frm.docname, "practitioner", data.message.name)
		}
	    }
	});
    },
    refresh: function(frm) {
	if(frm.doc.__islocal) {
	    frm.add_custom_button(__('Check Availability'), function() {
		check_availability_by_midwife(frm);
	    });
	}
    },
    appointment_type: function(frm){
	duration(frm);
    },
    date: function(frm){
	frappe.model.set_value(frm.doctype,frm.docname, 'start_dt', new Date(frm.doc.date + ' ' + frm.doc.start_time));
	frappe.model.set_value(frm.doctype,frm.docname, 'end_dt', new Date(moment(frm.doc.date + ' ' + frm.doc.start_time).add(frm.doc.duration, 'm')));
    },
    start_time: function(frm){
	frappe.model.set_value(frm.doctype,frm.docname, 'start_dt', new Date(frm.doc.date + ' ' + frm.doc.start_time));
	frappe.model.set_value(frm.doctype,frm.docname, 'end_dt', new Date(moment(frm.doc.date + ' ' + frm.doc.start_time).add(frm.doc.duration, 'm')));
    }
});


var duration = function(frm) {
    frappe.call({
	    "method": "frappe.client.get",
	    args: {
		doctype: "Midwife Appointment Type",
		name: frm.doc.appointment_type
	    },
	    callback: function (data) {
		frappe.model.set_value(frm.doctype,frm.docname, 'duration', data.message.duration);
		frappe.model.set_value(frm.doctype,frm.docname, 'end_dt', new Date(moment(frm.doc.date + ' ' + frm.doc.start_time).add(data.message.duration, 'm')));
	    }
    });
}

var check_availability_by_midwife = function(frm){
    if(frm.doc.practitioner && frm.doc.date){
	frappe.call({
	    method: "maia.maia.doctype.midwife_appointment.midwife_appointment.check_availability_by_midwife",
	    args: {practitioner: frm.doc.practitioner, date: frm.doc.date, time: frm.doc.start_time},
	    callback: function(r){
		/*show_availability(frm, r.message)*/
		console.log(r.message);
	    }
	});
    }else{
	msgprint("Please select a Practitioner and a Date");
    }
}

