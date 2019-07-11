frappe.provide('frappe.dashboards.chart_sources');

frappe.dashboards.chart_sources["Total consultations per week"] = {
	name: __("Total consultations per week"),
	method: "maia.maia.dashboard_chart_source.total_consultations_per_week.total_consultations_per_week.get",
	unit: "Consultations",
	color: "#77ecca",
	width: "Third",
	type: "Bar",
	timespan: "Last Year",
	timeseries: "1"
};