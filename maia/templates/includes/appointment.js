// Copyright (c) 2017,DOKOS and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide('maia.appointment');
var appointment = maia.appointment;

var config = {};

var source =  function(start, end, timezone, callback) {

    var appointment_type = $('#appointment_type option:selected').text();
    var practitioner_name = $('#practitioner option:selected').text();

	    return frappe.call({
		method: "maia.appointment.appointment.check_availabilities",
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
    
    $('#calendar').fullCalendar('removeEvent', source);
    $('#calendar').fullCalendar('addEvent', source);
    $('#calendar').fullCalendar('refetchEvents');

}

$('#appointment_type').on('change', loadEvents);
$('#practitioner').on('change', loadEvents);

$(document).ready(function() {

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
	    alert("Hello");
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

	// convert to user tz
	/*d.start = frappe.datetime.convert_to_user_tz(d.start);
	d.end = frappe.datetime.convert_to_user_tz(d.end);

	me.fix_end_date_for_event_render(d);*/

	var color_map = {
	    "danger": "red",
	    "success": "green",
	    "warning": "orange"
	};
	
	let color;
	if(me.get_css_class) {
	    color = color_map[me.get_css_class(d)];
	    // if invalid, fallback to blue color
	    if(!Object.values(color_map).includes(color)) {
		color = "blue";
	    }
	} else {
	    // color field can be set in {doctype}_calendar.js
	    // see event_calendar.js
	    color = d.color;
	}

	if(!color) color = "blue";
	d.className = "fc-bg-" + color;
	
	return d;
    });
}
