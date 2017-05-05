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
		if (!data.exe && data.message && data.message.name!=null) {
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
	    duration_and_color(frm);
    },
    date: function(frm){
	frappe.model.set_value(frm.doctype,frm.docname, 'start_dt', moment.utc(frm.doc.date + ' ' + frm.doc.start_time));
	frappe.model.set_value(frm.doctype,frm.docname, 'end_dt', moment.utc(frm.doc.date + ' ' + frm.doc.start_time).add(frm.doc.duration, 'm'));
    },
    start_time: function(frm){
	frappe.model.set_value(frm.doctype,frm.docname, 'start_dt', moment.utc(frm.doc.date + ' ' + frm.doc.start_time));
	frappe.model.set_value(frm.doctype,frm.docname, 'end_dt', moment.utc(frm.doc.date + ' ' + frm.doc.start_time).add(frm.doc.duration, 'm'));
    },
    patient_record: function(frm) {
	frappe.call({
	    "method": "frappe.client.get",
	    args: {
		doctype: "Patient Record",
		name: frm.doc.patient_record,
		fieldname: "email_id"
	    },
	    cache: false,
	    callback: function (data) {
		if  (data.message.email_id==null) {
		    frappe.model.set_value(frm.doctype, frm.docname, "email", __("Enter an Email Address"));
		    frm.set_df_property("email", "read_only", 0);
		} else if (!data.exe && data.message) {
		    frappe.model.set_value(frm.doctype, frm.docname, "email", data.message.email_id);
		    frm.set_df_property("email", "read_only", 1);
		}
	    }
	});
    }
});


var duration_and_color = function(frm) {
    if (frm.doc.appointment_type != null) {
    frappe.call({
	    "method": "frappe.client.get",
	    args: {
		doctype: "Midwife Appointment Type",
		name: frm.doc.appointment_type
	    },
	    callback: function (data) {
		frappe.model.set_value(frm.doctype,frm.docname, 'duration', data.message.duration);
		frappe.model.set_value(frm.doctype,frm.docname, 'end_dt', moment.utc(frm.doc.date + ' ' + frm.doc.start_time).add(data.message.duration, 'm'));
		frappe.model.set_value(frm.doctype,frm.docname, 'color', data.message.color);
	    }
    });
    }
}

var btn_update_status = function(frm, status){
    var doc = frm.doc;
    frappe.call({
	method:
	"maia.maia.doctype.midwife_appointment.midwife_appointment.update_status",
	args: {appointmentId: doc.name, status:status},
	callback: function(data){
	    if(!data.exc){
		cur_frm.reload_doc();
	    }
	}
    });
}

var check_availability_by_midwife = function(frm){
    if(frm.doc.practitioner && frm.doc.date && frm.doc.duration){
	frappe.call({
	    method: "maia.maia.doctype.midwife_appointment.midwife_appointment.check_availability_by_midwife",
	    args: {practitioner: frm.doc.practitioner, date: frm.doc.date, duration: frm.doc.duration},
	    callback: function(r){
		show_availability(frm, r.message)
	    }
	});
    }else{
	msgprint(__("Please select a Midwife, a Date and an Appointment Type"));
    }
}

var show_availability = function(frm, result){
    var d = new frappe.ui.Dialog({
	title: __("Midwife Availability"),
	fields: [
	    {
		fieldtype: "HTML", fieldname: "availability"
	    }
	]
    });
    var html_field = d.fields_dict.availability.$wrapper;
    html_field.empty();
    var list = ''
    $.each(result, function(i, v) {
	if(!v[0]){
	    $(repl('<div class="col-xs-12" style="padding-top:20px;">'+__("No Availability")+'</div></div>')).appendTo(html_field);
	    return
	}
	if(v[0]["msg"]){
	    var message = $(repl('<div class="col-xs-12" style="padding-top:20px;">%(msg)s</div></div>', {msg: v[0]["msg"]})).appendTo(html_field);
	    return
	}
	$(repl('<div class="col-xs-12 form-section-heading uppercase"><h6> %(practitioner)s</h6></div>', {practitioner: i})).appendTo(html_field);
	if(v[0][0]["start"]) {
	    var date = frappe.datetime.str_to_obj(v[0][0]["start"]);
	    var options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
	    $(repl('<div class="col-xs-12 border-bottom" style="margin-bottom: 0px; padding-top:15px; padding-bottom:10px; background-color: #f5f7fa; border: 1px solid #d1d8dd;"><h6> %(date)s</h6></div>', {date: date.toLocaleDateString('fr-FR', options)})).appendTo(html_field);
	     }
	$.each(result[i][0], function(x, y){
	    if(y["msg"]){
		var message = $(repl('<div class="col-xs-12" style="padding-top:12px; text-align:center;">%(msg)s</div></div>', {msg: y["msg"]})).appendTo(html_field);
		return
	    }
	    else{
		var start_time = frappe.datetime.str_to_obj(v[0][x]["start"]);
		var end_time = frappe.datetime.str_to_obj(v[0][x]["end"]);
		var row = $(repl('<div class="col-xs-12 list-customers-table border-left border-right border-bottom" style="padding-top:12px; text-align:center;" ><div class="col-xs-3"> %(start)s </div><div class="col-xs-2">-</div><div class="col-xs-3"> %(end)s </div><div class="col-xs-4"><a data-start="%(start)s" data-end="%(end)s" data-practitioner="%(practitioner)s"  href="#"><button class="btn btn-default btn-xs">'+__("Book")+'</button></a></div></div>', {start: start_time.toLocaleTimeString('fr-FR'), end: end_time.toLocaleTimeString('fr-FR'), practitioner: i})).appendTo(html_field);
	    }
	    row.find("a").click(function() {
		frm.doc.start_time = $(this).attr("data-start");
		refresh_field("start_time");
		frappe.model.set_value(frm.doctype,frm.docname, 'start_dt', moment.utc(frm.doc.date + ' ' + frm.doc.start_time));
		frappe.model.set_value(frm.doctype,frm.docname, 'end_dt', moment.utc(frm.doc.date + ' ' + frm.doc.start_time).add(frm.doc.duration, 'm'));
		d.hide()
		return false;
	    });
	})

	    });
    d.show();
}
