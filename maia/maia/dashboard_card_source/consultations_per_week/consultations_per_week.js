frappe.provide('frappe.dashboards.card_sources');

frappe.dashboards.card_sources["Consultations per week"] = {
	name: __("Consultations per week"),
	method: "maia.maia.dashboard_card_source.consultations_per_week.consultations_per_week.get",
	color: "#ff4081",
	icon: "fas fa-stethoscope"
};