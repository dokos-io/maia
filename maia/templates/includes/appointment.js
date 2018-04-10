// Copyright (c) 2018,DOKOS and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide('maia.appointment');

frappe.ready(function() {
	var selector = new maia.appointment.AppointmentSelector({
		parent: $('.page-head'),
	});
});

maia.appointment.AppointmentSelector = Class.extend({
	init(opts) {
		$.extend(this, opts);
		this.wrapper = this.parent.find('.page_content');
		this.make();

	},
	make: function() {
		var me = this;
		me.$selector_progress = $('<div>').addClass('selector-progress text-center text-extra-muted').prependTo($('#header-selector'));
		function selector_progress_dots() {
			for (let i = 1; i < 3; i++) {
				$(`<i class="fa fa-fw fa-circle"> </i>`).attr({'data-step-id': i}).appendTo(me.$selector_progress);
			}
		}
		selector_progress_dots();
		me.get_data();
	},
	get_data: function() {
		var me = this;
		frappe.call({
			method: "maia.templates.pages.appointment.get_practitioners_and_appointment_types",
			callback: (r) => {
				me.data = r.message;
				me.add_practitioner_section();
			}
		})
	},
	add_practitioner_section: function() {
		var me = this;
		$(frappe.render_template('practitioner_selector', {'data': me.data})).appendTo('#practitioner-selector');

		if (me.data.length == 1) {
			me.practitioner = me.data[0].name;
			me.update_progress_dots(1);
			me.add_appointment_types_section();
		}

		$(document).on('click', '.practitioner-option', e => {
			me.appointment_type = "";
			me.appointment_type_name = "";
			me.practitioner = $(e.target).attr('data-value');
			$(document).find('.practitioner-name').html('<h2>' + me.practitioner + '</h2>');
			me.update_progress_dots(1);
			me.add_appointment_types_section();
		})
	},
	add_appointment_types_section: function() {
		var me = this;
		$('#description').removeClass('bordered-top');
		$('#description').empty();

		let practitionerData = []
		me.data.forEach(function(value, index) {
			if (value.name == me.practitioner){
				value.appointment_types.forEach(function(value, index) {
					practitionerData.push({'name': value.name, 'appointment_type': value.appointment_type});
				})
			}
		});
		$('#appointment-type-selector').empty();
		$(frappe.render_template('appointment_type_selector', {'data': practitionerData})).appendTo('#appointment-type-selector');

		$(document).on('click', '.appointment-type-option', e => {
			me.appointment_type = $(e.target).attr('data-value');
			me.appointment_type_name = $(e.target).attr('display-value');
			$(document).find('.appointment-type-name').html('<h2>' + me.appointment_type_name + '</h2>');
			me.update_progress_dots(2);
			me.load_description();
			me.remove_events();
			if (me.calendar_loaded) {
				$('.bookpage').remove();
				me.refetch_events();
			} else {
				me.load_calendar();
				$('#calendar').show();
				$('#calendar').fullCalendar('render');
			}
		})
	},
	update_progress_dots: function(step) {
		var me = this;
		me.$selector_progress.find('i').removeClass('active');
		for (let i = 1; i < step + 1; i++) {
			me.$selector_progress.find(`[data-step-id='${i}']`).addClass('active');
		}
	},
	load_description: function() {
		var me = this;
		$('#description').empty();
		$('#description').removeClass('bordered-top');
		me.data.forEach(function(value, index) {
			if (value.name == me.practitioner) {
				value.appointment_types.forEach(function(value, index) {
					if (value.name == me.appointment_type) {
						me.appointment_type_description = value.description;
						me.group_appointment = value.group_appointment;
					}
				})
			}
		})

		if (me.appointment_type_description) {
			$('#description').html(me.appointment_type_description);
			$('#description').addClass('bordered-top');
		}
	},
	load_calendar: function() {
		var me = this;
		me.calendar_loaded = true;
		$('#calendar').removeClass('bg-grey');
		me.data.forEach(function(value, index) {
			if (value.name == me.practitioner) {
				me.week_end_booking = value.week_end;
			}
		});
		console.log(me)
		$('#calendar').fullCalendar({
			weekends: (me.week_end_booking == 0) ? false : true,
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
			minTime: "07:00:00",
			maxTime: "21:00:00",
			slotDuration: '00:15:00',
			scrollTime: '08:30:00',
			events: function(start, end, timezone, callback) {
				if (me.group_appointment==0) {
					frappe.call({
						method: "maia.templates.pages.appointment.check_availabilities",
						type: "GET",
						args: {
							"practitioner": me.practitioner,
							"start": moment(start).format("YYYY-MM-DD"),
							"end": moment(end).format("YYYY-MM-DD"),
							"appointment_type": me.appointment_type
						},
						callback: function(r) {
							var events = r.message;
							events.forEach(function(item) {
								me.prepare_events(item);
								if(callback) callback(item);
							});
						}
					})
				} else {
					frappe.call({
						method: "maia.templates.pages.appointment.check_group_events_availabilities",
						type: "GET",
						args: {
							"practitioner": me.practitioner,
							"start": moment(start).format("YYYY-MM-DD"),
							"end": moment(end).format("YYYY-MM-DD"),
							"appointment_type": me.appointment_type
						},
						callback: function(r) {
							var events = r.message;
							me.prepare_group_events(events);
							if(callback) callback(events);
						}
					})
				}
			},
			locale: 'fr',
			eventClick: function(event) {
				if (me.appointment_type) {
					me.show_booking_page(event)
				}
			},
		})
	},
	prepare_events: function(events) {
		var me = this;
		return (events || []).map(d => {
			d.id = d.name;
			d.editable = 0;

			var field_map = {
				"id": "id",
				"start": "start",
				"end": "end",
				"all_day": "allDay",
			};

			$.each(field_map, function(target, source) {
				d[target] = d[source];
			});

			if (!field_map.allDay)
				d.allDay = 0;

			return d;
		});
	},
	prepare_group_events: function(events) {
		var me = this;
		return (events || []).map(d => {
			if (d.seats_left == 0) {
				events.splice(events.indexOf(d), 1)
				return d
			}
			d.id = d.name;
			d.editable = 0;
			d.color = '';

			var field_map = {
				"id": "name",
				"start": "start_dt",
				"end": "end_dt",
				"all_day": "allDay",
			};

			$.each(field_map, function(target, source) {
				d[target] = d[source];
			});

			if (!field_map.allDay)
				d.allDay = 0;

			return d;
		});
	},
	remove_events: function() {
		$('#calendar').fullCalendar('removeEvents');
	},
	refetch_events: function() {
		$('#calendar').fullCalendar('refetchEvents');
	},
	destroy_calendar: function() {
		$('#calendar').fullCalendar('destroy');
	},
	show_booking_page: function(event) {
		var me = this;
		$('#calendar').fullCalendar('destroy');
		$('#calendar').addClass('bg-grey');
		let data = []
		data.push({'date': moment(event.start).format('LL'), 'start_time': moment(event.start).format('LT'), 'end_time': moment(event.end).format('LT'), 'appointment_type': me.appointment_type, 'appointment_type_display': me.appointment_type_name})
		if (event.seats_left) {
			$.extend(data[0], {'seats_left': event.seats_left})
		}
		$(frappe.render_template('booking_page', {'data': data})).appendTo('#calendar');

		$(document).on('click', '.bookpage-close', e => {
			$('#calendar').empty();
			me.load_calendar();
			$('#calendar').show();
			$('#calendar').fullCalendar('render');
		})

		$(document).on('submit', '.form', e => {
			e.preventDefault();

			var message = $('textarea[id="message"]').val();
			frappe.call({
				method: "maia.templates.pages.appointment.submit_appointment",
				type: "POST",
				cache: false,
				args: {
					email: "chdecultot@dokos.io",
					practitioner: me.practitioner,
					appointment_type: me.appointment_type,
					start: moment(event.start).format('YYYY-MM-DD H:mm:SS'),
					end: moment(event.end).format('YYYY-MM-DD H:mm:SS'),
					notes: message
				},
				callback: function(r) {
					if (r.message == "OK") {
						$('.bookpage').find('.bookpage-header').remove()
						$('.bookpage').find('.form').remove()
						$(__('<div class="bookpage-header"><h3 class="bookpage-thank-you">Merci.<br> Vous recevrez un email de confirmation dans quelques minutes.<h3><div>')).appendTo('.bookpage');
					} else {
						$('.bookpage').find('.bookpage-header').remove()
						$('.bookpage').find('.form').remove()
						$(__('<div class="bookpage-header"><h3 class="bookpage-thank-you">Un problème est survenu pendant l\'enregistrement de votre rendez-vous.<br>Veuillez rééssayer ou contacter votre professionnel(le).<h3><div>')).appendTo('.bookpage');
					}
				}
			})
			return false;
		})
	}

});
