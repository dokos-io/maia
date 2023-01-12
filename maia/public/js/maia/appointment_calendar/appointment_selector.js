// Copyright (c) 2020,DOKOS and Contributors
// See license.txt

import { Calendar } from '@fullcalendar/core';
import timeGridPlugin from '@fullcalendar/timegrid';
import listPlugin from '@fullcalendar/list';
import interactionPlugin from '@fullcalendar/interaction';
import dayGridPlugin from '@fullcalendar/daygrid';

frappe.provide('maia.appointment');
frappe.provide('maia.appointment_update');

maia.appointment.AppointmentSelector = class AppointmentSelector {
	constructor(opts) {
		Object.assign(this, opts);
		this.wrapper = this.parent.find('#calendar');
		this.midwife_selector = $('<div id="midwife-selector"></div>').appendTo($(this.wrapper));
		this.event_selector = $('<div id="event-selector"></div>').appendTo($(this.wrapper));
		this.event_confirmation = $('<div id="event-confirmation"></div>').appendTo($(this.wrapper));
		this.next_date_selector = $('<div id="next-date-selector"></div>').appendTo($(this.wrapper));
		this.practitioners = [];
		this.selected_practitioner = null;
		this.selected_appointment_category = null;
		this.selected_appointment_type = null;
		this.make();
	}

	make() {
		frappe.require([
			'/assets/js/moment-bundle.min.js',
			'/assets/js/control.min.js',
			'/assets/frappe/js/frappe/utils/datetime.js',
			'/assets/js/dialog.min.js'
		], () => {
			frappe.utils.make_event_emitter(maia.appointment_update);
			this.build_calendar()
		});
	}

	getPractitioners() {
		return frappe.call({
			method: "maia.templates.pages.appointment.get_practitioners_and_appointment_types"
		}).then((r) => {
				this.practitioners = r.message

				if (r.message.length===1) {
					this.selected_practitioner = r.message[0].name
				}
		})
	}

	build_calendar() {
		this.getPractitioners().then(() => {
			this.top_section = new maia.appointment.MidwifeSelector({parent: this})
			this.calendar_section = new maia.appointment.AppointmentCalendar({parent: this})
		});
	}

	is_group_appointment() {
		return this.selected_appointment_type ? this.practitioners
			.filter(f => f.name === this.selected_practitioner)
			.reduce((acc, val) => acc.concat(val.appointment_types), [])[0][this.selected_appointment_category]
			.filter(f => f.name === this.selected_appointment_type)[0].group_appointment
		: null
	}

}

maia.appointment.MidwifeSelector = class MidwifeSelector {
	constructor(opts) {
		Object.assign(this, opts)
		this.practitioners = this.parent.practitioners;
		this.render()
	}

	render() {
		const selectorEl = this.parent.midwife_selector;
		this.form = new frappe.ui.FieldGroup({
			fields: [
				{
					label: __('Midwife'),
					fieldname: 'midwife',
					fieldtype: 'Select',
					options: this.practitioners.map(f => f.name),
					change: () => {
						this.parent.selected_practitioner = this.form.get_value('midwife');
						this.form.set_df_property('category', 'hidden', 1);
						this.form.set_df_property('appointment_type', 'hidden', 1);
						this.set_categories();
						maia.appointment_update.trigger("update");
					},
				},
				{
					fieldtype: 'Column Break'
				},
				{
					label: __('Category'),
					fieldname: 'category',
					fieldtype: 'Select',
					options: [],
					hidden: 1,
					change: () => {
						this.parent.selected_appointment_category = this.form.get_value('category');
						this.set_appointment_types();
						maia.appointment_update.trigger("update")
					},
				},
				{
					fieldtype: 'Column Break'
				},
				{
					label: __('Appointment Type'),
					fieldname: 'appointment_type',
					fieldtype: 'Select',
					options: [],
					hidden: 1,
					change: () => {
						this.parent.selected_appointment_type = this.form.get_value('appointment_type');
						this.set_description();
						maia.appointment_update.trigger("update")
					},
				},
				{
					fieldtype: 'Section Break'
				},
				{
					fieldname: 'description',
					fieldtype: 'HTML',
					hidden: 1
				}
			],
			body: selectorEl[0]
		});
		this.form.make();
	}

	hide() {
		this.parent.midwife_selector.hide();
	}

	show() {
		this.parent.midwife_selector.show();
	}

	set_categories() {
		const categories = this.parent.selected_practitioner ? 
			this.practitioners
				.filter(f => f.name === this.parent.selected_practitioner)
				.reduce((acc, val) => acc.concat(val.categories), [])
			: []
		this.form.set_df_property('category', 'options', categories)
		let hidden = categories.length ? 0 : 1;
		this.form.set_df_property('category', 'hidden', hidden);
	}

	set_appointment_types() {
		const appointment_types= (this.parent.selected_practitioner&&this.parent.selected_appointment_category) ? 
			this.practitioners
				.filter(f => f.name === this.parent.selected_practitioner)
				.reduce((acc, val) => acc.concat(val.appointment_types), [])[0][this.parent.selected_appointment_category]
				.reduce((acc, val) => acc.concat(val.name), [])
			: []
		this.form.set_df_property('appointment_type', 'options', appointment_types)
		let hidden = appointment_types.length ? 0 : 1;
		this.form.set_df_property('appointment_type', 'hidden', hidden);
	}

	set_description() {
		const description = this.parent.selected_appointment_type ? this.practitioners
				.filter(f => f.name === this.parent.selected_practitioner)
				.reduce((acc, val) => acc.concat(val.appointment_types), [])[0][this.parent.selected_appointment_category]
				.filter(f => f.name === this.parent.selected_appointment_type)[0].description
			: null

		const html = `<div class="frappe-card">${description || ""}</div>`
		let hidden = description ? 0 : 1;
		this.form.set_df_property('description', 'hidden', hidden);
		!hidden && this.form.get_field("description").$wrapper.html(html);
	}
}

maia.appointment.AppointmentCalendar = class AppointmentCalendar {
	constructor(opts) {
		Object.assign(this, opts)
		this.fullCalendar = null;
		this.slots = []
		this.selected_slot = {};
		this.loading = false;
		this.render();
		maia.appointment_update.on("update", () => {
			this.fullCalendar ? this.refresh() : this.render();
		})
	}

	render() {
		if (this.parent.selected_practitioner && this.parent.selected_appointment_type) {
			const calendarEl = this.parent.event_selector;
			this.fullCalendar = new Calendar(
				calendarEl[0],
				this.calendar_options()
			)
			this.fullCalendar.render();
		}
	}

	get_initial_display_view() {
		return frappe.is_mobile() ? 'dayGridDay' : 'dayGridWeek'
	}

	set_initial_display_view() {
		this.fullCalendar.changeView(this.get_initial_display_view());
	}

	get_header_toolbar() {
		return {
			left: frappe.is_mobile() ? 'today' : 'dayGridWeek,listDay',
			center: 'prev,title,next',
			right: 'today',
		}
	}

	set_option(option, value) {
		this.fullCalendar.setOption(option, value);
	}

	destroy() {
		this.fullCalendar.destroy();
	}

	refresh() {
		this.fullCalendar.refetchEvents();
	}

	hide() {
		this.parent.event_selector.hide();
		this.parent.top_section.hide();
	}

	show() {
		this.parent.event_selector.show();
		this.parent.top_section.show();
	}

	calendar_options() {
		const me = this;
		return {
			eventClassNames: 'event-slot-calendar',
			initialView: me.get_initial_display_view(),
			headerToolbar: me.get_header_toolbar(),
			weekends: true,
			allDayContent: function() {
				return __("All Day");
			},
			buttonText: {
				today: __("Today"),
				timeGridWeek: __("Week"),
				listDay: __("Day")
			},
			plugins: [
				timeGridPlugin,
				listPlugin,
				interactionPlugin,
				dayGridPlugin
			],
			locale: frappe.boot.lang || 'en',
			timeZone: 'UTC',
			initialDate: moment().add(1,'d').format("YYYY-MM-DD"),
			noEventsContent: __("No events to display"),
			events: function(info, callback) {
				return me.getAvailableSlots(info, callback)
			},
			selectAllow: this.getSelectAllow,
			validRange: this.getValidRange,
			defaultDate: this.getDefaultDate,
			eventClick: function(event) {
				me.eventClick(event)
			}
		}
	}

	getAvailableSlots(parameters, callback) {
		frappe.call(this.slotAvailabilityMethod(), {
			start: moment(parameters.start).format("YYYY-MM-DD"),
			end: moment(parameters.end).format("YYYY-MM-DD"),
			practitioner: this.parent.selected_practitioner,
			appointment_type: this.parent.selected_appointment_type
		}).then(result => {
			this.slots = result.message || []

			if (!this.slots.length) {
				this.loading = true
				this.getNextAvailability(parameters.start)
			}

			callback(this.slots);
		})
	}

	getNextAvailability(start_dt) {
		if (start_dt && this.parent.selected_practitioner && this.parent.selected_appointment_type) {
			frappe.call({
				method: "maia.templates.pages.appointment.get_next_availability",
				type: "GET",
				args: {
					"practitioner": this.parent.selected_practitioner,
					"start": moment(start_dt).format("YYYY-MM-DD"),
					"appointment_type": this.parent.selected_appointment_type,
					"is_group": this.parent.is_group_appointment()
				}
			}).then(r => {
				if (r.message.status) {
					new maia.appointment.NextDateSelector({parent: this, next_date: r.message.date, next_date_status: r.message.status})
				}
			})
		}
	}

	eventClick(event) {
		this.selected_slot = event.event
		new maia.appointment.SlotConfirmation({parent: this})
	}

	cancelEventSelection() {
		this.selected_slot = null
		this.message = ""
	}

	slotAvailabilityMethod() {
		return this.parent.is_group_appointment() ? "maia.templates.pages.appointment.check_group_events_availabilities" : "maia.templates.pages.appointment.check_availabilities"
	}

	submitEvent() {
		this.btn_disabled = true
		frappe.call({
			method: "maia.templates.pages.appointment.submit_appointment",
			args: {
				email: frappe.session.user,
				practitioner: this.parent.selected_practitioner,
				appointment_type: this.parent.selected_appointment_type,
				start: moment(this.selected_slot.start).format('YYYY-MM-DD H:mm:SS'),
				end: moment(this.selected_slot.end).format('YYYY-MM-DD H:mm:SS'),
				notes: this.message
			}
		}).then(r => {
			this.btn_disabled = false
			this.$refs.fullCalendar.getApi().refetchEvents();
			this.cancelEventSelection()
			const message = r.message.appointment ? __("Thank you ! You will receive a confirmation message in a few minutes.")
				: __("An unexpected error prevented the submission of your request. Please contact your midfiwe directly.")
			const indicator = r.message.appointment ? "green" : "red"
			frappe.show_alert({ message: message, indicator:  indicator})
		})
	}

	getTimeZone() {
		frappe.call("frappe.core.doctype.system_settings.system_settings.get_timezone")
		.then(r => {
			this.fullCalendar.setOption("timeZone", r.message);
		})
	}

	getSelectAllow(selectInfo) {
		return moment().diff(selectInfo.start) <= 0
	}

	getValidRange() {
		return { start: moment().add(1,'d').format("YYYY-MM-DD") }
	}

	formatted_date(dt) {
		return moment(dt).locale('fr').format("LL")
	}
}

maia.appointment.SlotConfirmation = class SlotConfirmation {
	constructor(opts) {
		Object.assign(this, opts)
		this.event = this.parent.selected_slot;
		this.btn_disabled = false;
		this.render()
	}

	render() {
		const html = `
			<div class="appointment-modal">
				<div class="appointment-modal-close"><i class="fas fa-times"></i></div>
				<div class="appointment-modal-header">
					<h2 class="appointment-modal-date">${this.parent.formatted_date(this.event.start)}</h2>
					<h3 class="appointment-modal-time">${this.formatted_time(this.event.start)} - ${this.formatted_time(this.event.end)}</h3>
				</div>
				<div class="appointment-modal-header">
					<h2 class="appointment-modal-appointment-type">${this.parent.parent.selected_appointment_type}</h2>
					<h3 class="appointment-modal-seats-left hidden">${ this.parent.seats_left || 0 } ${ this.parent.seats_left === 1 ? __("Remaining seat") : __("Remaining seats") }</h3>
				</div>
				<div class="form">
					<div class="form-box">
						<div class="form-fields">
							<textarea id="message" class="form-input" rows="3" name="message" placeholder="${__('Your message')}"></textarea>
						</div>
					</div>
					<button class="form-button">${ __("Confirm") }</button>
				</div>
			</div>
		`

		this.parent.parent.is_group_appointment() && $(".appointment-modal-seats-left").removeClass("hidden");
		this.parent.hide();
		this.parent.parent.event_confirmation.html(html);
		this.bind_events()
	}

	bind_events() {
		$('.appointment-modal-close').on('click', e => {
			e.preventDefault();
			this.destroy();
			this.parent.show();
		})

		$('.form-button').on('click', e => {
			e.preventDefault();
			$('.form-button').text(__("Confirmation..."))
			$('.form-button').attr("disabled", true);
			this.submitEvent();
		})
	}

	submitEvent() {
		frappe.call({
			method: "maia.templates.pages.appointment.submit_appointment",
			args: {
				email: frappe.session.user,
				practitioner: this.parent.parent.selected_practitioner,
				appointment_type: this.parent.parent.selected_appointment_type,
				start: moment(this.event.start).format('YYYY-MM-DD H:mm:SS'),
				end: moment(this.event.end).format('YYYY-MM-DD H:mm:SS'),
				notes: $('#message').val()
			}
		}).then(r => {
			this.parent.refresh();
			this.parent.selected_slot = null
			const message = r.message.appointment ? __("Thank you ! You will receive a confirmation message in a few minutes.")
				: __("An unexpected error prevented the submission of your request. Please contact your midfiwe directly.")
			const indicator = r.message.appointment ? "green" : "red"
			frappe.show_alert({ message: message, indicator:  indicator})
			this.destroy();
			this.parent.show();
		})
	}

	destroy() {
		this.parent.parent.event_confirmation.html("");
	}

	formatted_time(dt) {
		return moment(dt).locale('fr').format("LT")
	}
}

maia.appointment.NextDateSelector = class NextDateSelector {
	constructor(opts) {
		Object.assign(this, opts)
		this.render()
	}

	render() {
		const innerHtml = this.next_date_status === 200 ? `
			<div class="appointment-modal-header">
				<h2 class="appointment-modal-title">${ __("The next available slot is on:") }</h2>
				<h2 class="appointment-modal-date">${ this.parent.formatted_date(this.next_date) }</h2>
			</div>
			<button class="form-button">${ __("See this date") }</button>
		` : `
			<div class="appointment-modal-close"><i class="fas fa-times"></i></div>
			<div class="appointment-modal-header">
				<h2 class="appointment-modal-title pt-5">${ __('No additional slots available for this appointment type') }</h2>
			</div>
		`
		const html = `
			<div class="appointment-modal">
				${innerHtml}
			</div>
		`
		this.parent.hide();
		this.parent.parent.next_date_selector.html(html);
		this.bind_events()
	}

	destroy() {
		this.parent.parent.next_date_selector.html("");
	}

	bind_events() {
		$('.appointment-modal-close').on('click', e => {
			e.preventDefault();
			this.destroy();
			this.parent.fullCalendar.gotoDate(moment().add(1,'d').format("YYYY-MM-DD"));
			this.parent.show();
		})

		$('.form-button').on('click', e => {
			e.preventDefault();
			this.goToNextDate();
		})
	}

	goToNextDate() {
		this.parent.fullCalendar.gotoDate(this.next_date);
		this.parent.refresh();
		this.destroy();
		this.parent.show();
	}
}