frappe.provide('frappe.dashboards.card_sources');

frappe.dashboards.card_sources["Total Revenue"] = {
	name: __("Total Revenue"),
	method: "maia.maia_accounting.dashboard_card_source.total_revenue.total_revenue.get",
	color: "#3498db",
	icon: "fas fa-chart-line",
	timespan: "Last Year"
};