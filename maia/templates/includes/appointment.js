// Copyright (c) 2018,DOKOS and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide('maia.appointment');
//var appointment = maia.appointment;


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
					practitionerData.push(value.name);
				})
			}
		});
		$('#appointment-type-selector').empty();
		$(frappe.render_template('appointment_type_selector', {'data': practitionerData})).appendTo('#appointment-type-selector');

		$(document).on('click', '.appointment-type-option', e => {
			$('.bookpage').remove();
			me.remove_events();
			me.appointment_type = $(e.target).attr('data-value');
			$(document).find('.appointment-type-name').html('<h2>' + me.appointment_type + '</h2>');
			me.load_description();
			me.update_progress_dots(2);
			me.load_calendar();
			me.refetch_events();
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
		frappe.call({
			method: "frappe.client.get",
			type: "GET",
			args: {
				"doctype": "Maia Appointment Type",
				"name": me.appointment_type,
			},
			callback: function(r) {
				description = r.message.description;
				$('#description').html(description);
				$('#description').addClass('bordered-top');
			}
		})
	},
	load_calendar: function() {
		var me = this;
		$('#calendar').removeClass('bg-grey');
		frappe.call({
			method: "frappe.client.get",
			type: "GET",
			args: {
				"doctype": "Professional Information Card",
				"name": me.practitioner,
				fields: ["weekend_booking"]
			},
			callback: function(r) {
				$('#calendar').fullCalendar({
					weekends: (r.message.weekend_booking == 0) ? false : true,
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
					events: function(start, end, timezone, callback) {
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
					},
					locale: 'fr',
					eventClick: function(event) {
						me.show_booking_page(event)
					},
				})
			}
		});
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
				"allDay": "all_day",
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
		data.push({'date': moment(event.start).format('LL'), 'start_time': moment(event.start).format('LT'), 'end_time': moment(event.end).format('LT'), 'appointment_type': me.appointment_type})
		$(frappe.render_template('booking_page', {'data': data})).appendTo('#calendar');

		$(document).on('click', '.bookpage-close', e => {
			$('#calendar').empty();
			me.load_calendar();
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
		})
	}

});
