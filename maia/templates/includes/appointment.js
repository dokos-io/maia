// Copyright (c) 2017,DOKOS and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide('maia.appointment');
var appointment = maia.appointment;

var load_description =  function() {
    var appointment_type = $('#appointment_type option:selected').text();

    frappe.call({
	method: "frappe.client.get",
	type: "GET",
	args: {
	    doctype: "Midwife Appointment Type",
	    name: appointment_type
	},
	callback: function(r) {
	    description = r.message.description;
	    $("#description").text(description);
	}
    })

    
}

var source =  function(start, end, timezone, callback) {

    var appointment_type = $('#appointment_type option:selected').text();

    if(!$('#practitioner').is("select")) {
	var practitioner_name = $('#practitioner').text();
    } else {
	var practitioner_name = $('#practitioner option:selected').text();
    }
    return frappe.call({
	method: "maia.templates.pages.appointment.check_availabilities",
	type: "GET",
	args: {
	    "practitioner": practitioner_name,
	    "start": moment(start).format("YYYY-MM-DD"),
	    "end": moment(end).format("YYYY-MM-DD"),
	    "appointment_type": appointment_type 
	},
	callback: function(r) {
		   
	    var events = r.message;
	    events.forEach(function(item) {
		prepare_events(item);
		callback(item);
	    });
	}
    })
};


function loadEvents() {
    load_description()
    $('#calendar').fullCalendar('removeEvent', source);
    $('#calendar').fullCalendar('addEvent', source);
    $('#calendar').fullCalendar('refetchEvents');

}

$('#appointment_type').on('change', loadEvents);
$('#practitioner').on('change', loadEvents);

$(document).ready(function() {
    load_description()
    
    $('#calendar').fullCalendar({
	weekends: false,
	header: {
	    left: 'title',
	    center: '',
	    right: 'prev,next agendaWeek,agendaDay'
	},
	defaultView: "agendaWeek",
	editable: true,
	selectable: true,
	selectHelper: true,
	forceEventDuration: true,
	allDaySlot: false,
	minTime: "08:00:00",
	maxTime: "24:00:00",
	events: source,
	eventClick: function(event) {
	    showBookingPage(event);
	},
    })

});


var prepare_events = function(events) {
    var me = this;
    
    return (events || []).map(d => {
	d.id = d.name;
	d.editable = 0;

	var field_map =  {
	    "id": "id",
	    "start": "start",
	    "end": "end",
	    "allDay": "all_day",
	};
	
	$.each(field_map, function(target, source) {
	    d[target] = d[source];
	});

	if(!field_map.allDay)
	    d.allDay = 0;
	
	return d;
    });
}

var showBookingPage = function(eventData) {
     var appointment_type = $('#appointment_type option:selected').text();

    if(!$('#practitioner').is("select")) {
	var practitioner_name = $('#practitioner').text();
    } else {
	var practitioner_name = $('#practitioner option:selected').text();
    }
    
    frappe.call({
	method: "maia.templates.pages.appointment.submit_appointment",
	type: "POST",
	args: {
	    patient_record: "Augustine Dupond",
	    practitioner: practitioner_name,
	    appointment_type: appointment_type,
	    start: moment(eventData.start).format('YYYY-MM-DD H:mm:SS'),
	    end: moment(eventData.end).format('YYYY-MM-DD H:mm:SS')
	},
	callback: function(r) {
	    loadEvents()	
	}
    })
    
}
