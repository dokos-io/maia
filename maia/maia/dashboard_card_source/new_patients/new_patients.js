frappe.provide('frappe.dashboards.card_sources');

frappe.dashboards.card_sources["New Patients"] = {
	name: __("New Patients"),
	method: "maia.maia.dashboard_card_source.new_patients.new_patients.get",
	color: "#ff4081",
	icon: "fas fa-users"
};