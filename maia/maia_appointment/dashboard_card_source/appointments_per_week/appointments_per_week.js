
frappe.provide('frappe.dashboards.card_sources');

frappe.dashboards.card_sources["Appointments per week"] = {
	name: __("Appointments per week"),
	method: "maia.maia_appointment.dashboard_card_source.appointments_per_week.appointments_per_week.get",
	color: "#8e44ad",
	icon: "octicon octicon-calendar"
};