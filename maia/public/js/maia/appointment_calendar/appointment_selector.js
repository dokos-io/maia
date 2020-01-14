// Copyright (c) 2019,DOKOS and Contributors
// See license.txt
import AppointmentCalendar from './appointment_calendar.vue';

frappe.provide('maia.appointment');
frappe.provide('maia.appointment_update');

maia.appointment.AppointmentSelector = class AppointmentSelector {
	constructor(opts) {
		Object.assign(this, opts);
		this.wrapper = this.parent.find('#calendar');
		this.make();
	}

	make() {
		frappe.require([
			'/assets/js/frappe-vue.min.js',
			'/assets/js/moment-bundle.min.js',
			'/assets/js/control.min.js'
		], () => {
			frappe.utils.make_event_emitter(maia.appointment_update);
			this.build_calendar()
		});
    }

    build_calendar() {
		new Vue({
			el: this.wrapper[0],
			render: h => h(AppointmentCalendar)
		})
	}

}