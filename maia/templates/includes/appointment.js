// Copyright (c) 2017,DOKOS and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide('maia.appointment');
var appointment = maia.appointment;

frappe.ready(function() {
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
		minTime: "06:00:00",
		maxTime: "24:00:00",
		slotDuration: '00:15:00',
		scrollTime: '08:30:00',
		events: source,
		locale: 'fr',
		eventClick: function(event) {
			showBookingPage(event);
		},
	})

	$('#modal').iziModal({
		title: 'Confirmer votre rendez-vous ?',
		subtitle: '',
		headerColor: '#ff79a6',
		theme: '', // light
		appendTo: '.body', // or false
		icon: null,
		iconText: null,
		iconColor: '',
		rtl: false,
		width: 600,
		top: null,
		bottom: null,
		borderBottom: true,
		padding: 0,
		radius: 3,
		zindex: 11,
		iframe: false,
		iframeHeight: 400,
		iframeURL: null,
		focusInput: true,
		group: '',
		loop: false,
		navigateCaption: true,
		navigateArrows: true, // Boolean, 'closeToModal', 'closeScreenEdge'
		history: false,
		restoreDefaultContent: true,
		autoOpen: 0, // Boolean, Number
		bodyOverflow: false,
		fullscreen: false,
		openFullscreen: false,
		closeOnEscape: true,
		closeButton: true,
		overlay: true,
		overlayClose: true,
		overlayColor: 'rgba(0, 0, 0, 0.4)',
		timeout: false,
		timeoutProgressbar: false,
		pauseOnHover: false,
		timeoutProgressbarColor: 'rgba(255,255,255,0.5)',
		transitionIn: 'comingIn',
		transitionOut: 'comingOut',
		transitionInOverlay: 'fadeIn',
		transitionOutOverlay: 'fadeOut',
		onFullscreen: function() {},
		onResize: function() {},
		onOpening: function() {},
		onOpened: function() {},
		onClosing: function() {},
		onClosed: function() {}
	});

	$("#confirmation").iziModal({
		title: 'Rendez-Vous Confirmé',
		headerColor: '#ff79a6',
		overlayColor: 'rgba(0, 0, 0, 0.6)',
		overlayClose: true,
		closeOnEscape: true,
		bodyOverflow: false,
		focusInput: true,
		autoOpen: false,
		fullscreen: false,
		openFullscreen: false,
		bottom: 0,
		timeout: 5000,
		timeoutProgressbar: true,
		timeoutProgressbarColor: '#ff4081',
		transitionInModal: 'transitionIn',
		transitionOutModal: 'transitionOut',
		transitionInOverlay: 'fadeIn',
		transitionOutOverlay: 'fadeOut',
	});

	$('#appointment_type').on('change', loadEvents);
	$('#practitioner').on('change', get_appointment_types);

});

var load_description = function() {
	var appointment_type = $('#appointment_type option:selected').text();

	frappe.call({
		method: "frappe.client.get",
		type: "GET",
		args: {
			"doctype": "Midwife Appointment Type",
			"name": appointment_type,
		},
		callback: function(r) {
			description = r.message.description;
			$("#description").html(description);
		}
	})


}

var source = function(start, end, timezone, callback) {

	var appointment_type = $('#appointment_type option:selected').text();

	if (!$('#practitioner').is("select")) {
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


var prepare_events = function(events) {
	var me = this;

	return (events || []).map(d => {
		d.id = d.name;
		d.editable = 0;

		var field_map = {
			"id": "id",
			"start": "start",
			"end": "end",
			"allDay": "all_day",
		};

		$.each(field_map, function(target, source) {
			d[target] = d[source];
		});

		if (!field_map.allDay)
			d.allDay = 0;

		return d;
	});
}

var get_appointment_types = function() {
	if (!$('#practitioner').is("select")) {
		var practitioner_name = $('#practitioner').text();
	} else {
		var practitioner_name = $('#practitioner option:selected').text();
	}

	return frappe.call({
		method: "frappe.client.get_list",
		type: "GET",
		args: {
			"doctype": "Midwife Appointment Type",
			fields: ["name", "practitioner"]
		},
		callback: function(r) {

			var types = r.message.sort(compare);
			var message;
			types.forEach(function(item) {
				if (item.practitioner == practitioner_name || item.practitioner == null) {
					message += "<option>" + item.name + "</option>"
				}
			});
			$('#appointment_type').html(message);
		}
	});
	loadEvents();
}

var showBookingPage = function(eventData) {
	var appointment_type = $('#appointment_type option:selected').text();
	$("#modal").iziModal("open");
	$('#modal').iziModal('setTitle', 'Confirmer votre rendez-vous "' + appointment_type + '" ?');
	$('#modal').iziModal('setSubtitle', moment(eventData.start).locale('fr').format('LLLL'));

	$("#modal").off('click', ".submit").on('click', '.submit', function() {
		submitBookingForm(eventData);
		$("#modal").iziModal("close");
	});
}


var submitBookingForm = function(eventData) {
	var appointment_type = $('#appointment_type option:selected').text();

	if (!$('#practitioner').is("select")) {
		var practitioner_name = $('#practitioner').text();
	} else {
		var practitioner_name = $('#practitioner option:selected').text();
	}

	var message = $('input[id="message"]').val();
	frappe.call({
		method: "maia.templates.pages.appointment.submit_appointment",
		type: "POST",
		cache: false,
		args: {
			email: frappe.session.user,
			practitioner: practitioner_name,
			appointment_type: appointment_type,
			start: moment(eventData.start).format('YYYY-MM-DD H:mm:SS'),
			end: moment(eventData.end).format('YYYY-MM-DD H:mm:SS'),
			notes: message
		},
		callback: function(r) {
			if (r.message == "OK") {
				loadEvents(eventData);
				$("#confirmation").iziModal("open");
			}
		}
	})
};


function loadEvents(source) {
	load_description()
	$('#calendar').fullCalendar('removeEvents');
	$('#calendar').fullCalendar('refetchEvents');
}

function compare(a, b) {
	// Use toUpperCase() to ignore character casing
	const nameA = a.name.toUpperCase();
	const nameB = b.name.toUpperCase();

	let comparison = 0;
	if (nameA > nameB) {
		comparison = 1;
	} else if (nameA < nameB) {
		comparison = -1;
	}
	return comparison;
}
