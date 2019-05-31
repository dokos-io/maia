frappe.provide('frappe.dashboards.card_sources');

frappe.dashboards.card_sources["Without Codification Percentage"] = {
	method: "maia.maia_accounting.dashboard_card_source.without_codification_percentage.without_codification_percentage.get",
	color: "#3498db",
	icon: "fa fa-flag-o",
	timespan: "Preregistered"
};