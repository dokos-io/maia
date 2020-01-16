// Copyright (c) 2019,DOKOS and Contributors
// See license.txt

frappe.provide('maia.appointment');

frappe.ready(function() {
	new maia.appointment.AppointmentSelector({
		parent: $('.page_content'),
	});
});