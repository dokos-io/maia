frappe.provide('frappe.dashboards.chart_sources');

frappe.dashboards.chart_sources["Codifications repartition"] = {
	name: __("Codifications repartition"),
	method: "maia.maia_accounting.dashboard_chart_source.codifications_repartition.codifications_repartition.get",
	unit: "Consultations",
	color: "#ecc077",
	width: "Third",
	type: "Bar",
	timespan: "Last Year"
};