frappe.provide('frappe.dashboards.card_sources');

frappe.dashboards.card_sources["Patient outstanding amount"] = {
	name: __("Patient outstanding amount"),
	method: "maia.maia_accounting.dashboard_card_source.patient_outstanding_amount.patient_outstanding_amount.get",
	color: "#3498db",
	icon: "fa fa-eur",
	timespan: "Custom"
};