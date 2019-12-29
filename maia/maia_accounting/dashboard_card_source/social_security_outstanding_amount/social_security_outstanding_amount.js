frappe.provide('frappe.dashboards.card_sources');

frappe.dashboards.card_sources["Social security outstanding amount"] = {
	name: __("Social security outstanding amount"),
	method: "maia.maia_accounting.dashboard_card_source.social_security_outstanding_amount.social_security_outstanding_amount.get",
	color: "#3498db",
	icon: "fas fa-hourglass-end",
	timespan: "All Time"
};