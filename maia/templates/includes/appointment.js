// Copyright (c) 2019,DOKOS and Contributors
// See license.txt

frappe.provide('maia.appointment');

frappe.ready(function() {
	new maia.appointment.AppointmentSelector({
		parent: $('.page-head'),
	});
});

maia.appointment.AppointmentSelector = class AppointmentSelector {
	constructor(opts) {
		$.extend(this, opts);
		this.wrapper = this.parent.find('.page_content');
		this.make();
		moment.locale('fr');
	}

	make() {
		var me = this;
		me.$selector_progress = $('<div>').addClass('selector-progress mx-auto text-extra-muted').appendTo($('#selector-steps'));
		me.get_data();
	}

	selector_progress_dots() {
		var me = this;
		me.$selector_progress.empty();
		for (let i = 1; i < me.steps + 1; i++) {
			$(`<i class="fas fa-fw fa-circle"> </i>`).attr({'data-step-id': i}).appendTo(me.$selector_progress);
		}
	}

	get_data() {
		var me = this;
		frappe.call({
			method: "maia.templates.pages.appointment.get_practitioners_and_appointment_types",
			callback: (r) => {
				me.data = r.message;
				me.add_practitioner_section();
			}
		})
	}

	add_practitioner_section() {
		var me = this;
		$(frappe.render_template('practitioner_selector', {'data': me.data})).appendTo('#practitioner-selector');

		me.steps = 2;
		me.selector_progress_dots();

		if (me.data.length == 1) {
			me.practitioner = me.data[0].name;
			me.update_progress_dots();
			me.add_category_section();
		}

		$(document).on('click', '.practitioner-option', e => {
			me.clear_custom_pages();
			me.appointment_type = "";
			me.appointment_type_name = "";
			me.group_appointment = 0;
			me.practitioner = $(e.target).attr('data-value');
			$(document).find('.practitioner-name').html('<h4>' + me.practitioner + '</h4>');
			me.step = 1;
			me.add_category_section();
			me.update_progress_dots();
		})
	}

	add_appointment_types_section() {
		var me = this;
		$('#description').removeClass('bordered-top');
		$('#description').empty();

		let practitionerData = []
		me.data.forEach(function(value, index) {
			if (value.name == me.practitioner){
				value.appointment_types[me.category].forEach(function(value, index) {
					practitionerData.push({'name': value.name, 'appointment_type': value.appointment_type});
				})
			}
		});
		$('#appointment-type-selector').empty();
		$(frappe.render_template('appointment_type_selector', {'data': practitionerData})).appendTo('#appointment-type-selector');

		$(document).on('click', '.appointment-type-option', e => {
			me.appointment_type = $(e.target).attr('data-value');
			me.appointment_type_name = $(e.target).attr('display-value');
			$(document).find('.appointment-type-name').html('<h4>' + me.appointment_type_name + '</h4>');
			me.step = 3
			me.update_progress_dots();
			me.load_description();
			me.destroy_calendar();
			$('.next-availability').remove();
			$('.bookpage').remove();
			me.load_calendar();
		})
	}

	add_category_section() {
		var me = this;
		$(document).find('#category-selector').remove();
		$('#appointment-type-selector').empty();

		me.data.forEach(function(value, index) {
			if (value.name == me.practitioner){
				if (value.categories.length < 2 ) {
					me.category = value.categories[0];
					me.add_appointment_types_section();
				} else {
					me.steps = 3;
					me.selector_progress_dots();
					$('<div class="col-sm-4 col-12 h6 text-uppercase" id="category-selector"></div>').insertAfter($('#practitioner-selector'))
					$(frappe.render_template('category_selector', {'data': value.categories})).appendTo('#category-selector');
				}
			}
		});

		$(document).on('click', '.category-option', e => {
			me.remove_events();
			me.category = $(e.target).attr('data-value');
			$(document).find('.category-name').html('<h4>' + me.category + '</h4>');
			me.step = 2;
			me.update_progress_dots();
			me.add_appointment_types_section();
		})

	}

	update_progress_dots() {
		var me = this;
		me.$selector_progress.find('i').removeClass('active');
		for (let i = 1; i < me.step + 1; i++) {
			me.$selector_progress.find(`[data-step-id='${i}']`).addClass('active');
		}
	}

	load_description() {
		var me = this;
		$('#description').empty();
		$('#description').removeClass('bordered-top');
		me.data.forEach(function(value, index) {
			if (value.name == me.practitioner) {
				value.appointment_types[me.category].forEach(function(value, index) {
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
	}

	load_calendar(default_date=moment()) {
		var me = this;
		$('#calendar').removeClass('bg-grey');
		me.data.forEach(function(value, index) {
			if (value.name == me.practitioner) {
				me.week_end_booking = value.week_end;
			}
		});
		$('#calendar').fullCalendar({
			weekends: (me.week_end_booking == 0) ? false : true,
			header: {
				left: 'title',
				center: '',
				right: 'prev,next agendaWeek,agendaDay'
			},
			defaultView: "agendaWeek",
			selectHelper: true,
			forceEventDuration: true,
			height: 1000,
			contentHeight: 1000,
			handleWindowResize: false,
			allDaySlot: false,
			minTime: "07:00:00",
			maxTime: "21:00:00",
			slotDuration: '00:15:00',
			scrollTime: '08:30:00',
			defaultDate: default_date,
			events: function(start, end, timezone, callback) {
				if (me.appointment_type) {
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
								if (!events[0].length) {
									me.get_next_availability(start, 0); 
								} else {
									events.forEach(function(item) {
										me.prepare_events(item);
										if(callback) callback(item);
									});
								}
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
								if (events == undefined) {
									me.get_next_availability(start, 1);
								}
								if (events) {
									me.prepare_group_events(events);
									if(callback) callback(events);
								}
							}
						})
					}
				}
			},
			locale: 'fr',
			eventClick: function(event) {
				if (me.appointment_type) {
					me.show_booking_page(event)
				}
			},
		})
		$('#calendar').removeClass('d-none');
		$('#calendar').fullCalendar('render');
	}

	get_next_availability(start, isGroup) {
		let me = this;
		frappe.call({
			method: "maia.templates.pages.appointment.get_next_availability",
			type: "GET",
			args: {
				"practitioner": me.practitioner,
				"start": moment(start).format("YYYY-MM-DD"),
				"appointment_type": me.appointment_type,
				"is_group": isGroup
			},
			callback: function(r) {
				if (r.message) {
					r.message.formatted_date = moment(r.message.date).format('LL');
					me.show_next_availability_page(r.message);
				}
			}
		})
	}

	show_next_availability_page(message) {
		let me = this;
		me.next_date = message;
		$('#calendar').fullCalendar('destroy');
		$('#calendar').addClass('bg-grey');
		$('#calendar').html(frappe.render_template('next_availability_page', {'data': me.next_date}));

		$(document).on('click', '.next-availability-close', e => {
			e.stopImmediatePropagation();
			me.clear_custom_pages();
		})

		$(document).on('click', '.next-availability-button', e => {
			e.stopImmediatePropagation();
			$('#calendar').empty();
			me.load_calendar(me.next_date.date);
		})
	}

	prepare_events(events) {
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
	}

	prepare_group_events(events) {
		var me = this;
		return (events || []).map(d => {
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
	}

	remove_events() {
		$('#calendar').fullCalendar('removeEvents');
	}

	refetch_events() {
		$('#calendar').fullCalendar('refetchEvents');
	}

	destroy_calendar() {
		$('#calendar').fullCalendar('destroy');
	}

	show_booking_page(event) {
		var me = this;
		me.event = event;
		$('#calendar').fullCalendar('destroy');
		$('#calendar').addClass('bg-grey');
		let data = []
		data.push({'date': moment(event.start).format('LL'), 'start_time': moment(event.start).format('LT'), 'end_time': moment(event.end).format('LT'), 'appointment_type': me.appointment_type, 'appointment_type_display': me.appointment_type_name})
		if (event.seats_left) {
			$.extend(data[0], {'seats_left': event.seats_left})
		}
		$('#calendar').html(frappe.render_template('booking_page', {'data': data}));

		$(document).on('click', '.bookpage-close', e => {
			e.stopImmediatePropagation();
			me.clear_custom_pages();
		})

		$(document).on('submit', '.form', e => {
			e.preventDefault();

			let $btn = $('.form-button')
			$btn.prop("disabled", true).addClass('btn-loading').html("Confirmation ...");
			var message = $('textarea[id="message"]').val();
			frappe.call({
				method: "maia.templates.pages.appointment.submit_appointment",
				type: "POST",
				cache: false,
				args: {
					email: frappe.session.user,
					practitioner: me.practitioner,
					appointment_type: me.appointment_type,
					start: moment(me.event.start).format('YYYY-MM-DD H:mm:SS'),
					end: moment(me.event.end).format('YYYY-MM-DD H:mm:SS'),
					notes: message
				},
				callback: function(r) {
					if (r.message == "OK") {
						$btn.removeClass('btn-loading').addClass('btn-confirmed').html("Succès");
						$('.bookpage').find('.form-box').empty()
						$(__('<div class="form-confirmation-container"><div class="form-confirmation"><h3 class="bookpage-thank-you">Merci.<br> Vous recevrez un email de confirmation dans quelques minutes.<h3><div></div>')).appendTo('.form-box');
					} else {
						$btn.removeClass('btn-loading').addClass('btn-error').html("Erreur");
						$('.bookpage').find('.form-box').empty()
						$(__('<div class="form-confirmation-container"><div class="form-confirmation"><h3 class="bookpage-thank-you">Un problème est survenu pendant l\'enregistrement de votre rendez-vous.<br>Veuillez rééssayer ou contacter votre professionnel(le).<h3><div></div>')).appendTo('.form-box');
					}
				}
			})
			e.stopImmediatePropagation();
			return false;
		})
	}

	clear_custom_pages() {
		let me = this;
		$('#calendar').empty();
		me.load_calendar();
	}

}
