frappe.provide('frappe.dashboards.card_sources');

frappe.dashboards.card_sources["Outstanding reconciliations"] = {
	name: __("Outstanding reconciliations"),
	method: "maia.maia_accounting.dashboard_card_source.outstanding_reconciliations.outstanding_reconciliations.get",
	color: "#3498db",
	icon: "fa fa-calculator",
	timespan: "Custom"
};