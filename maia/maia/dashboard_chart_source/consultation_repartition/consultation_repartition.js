frappe.provide('frappe.dashboards.chart_sources');

frappe.dashboards.chart_sources["Consultation Repartition"] = {
	method: "maia.maia.dashboard_chart_source.consultation_repartition.consultation_repartition.get",
	unit: __("Consultations"),
	color: "#77ecca",
	width: "Third",
	type: "Bar"
};