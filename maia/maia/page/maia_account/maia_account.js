frappe.provide("maia");

frappe.pages['maia-account'].on_page_load = function(wrapper) {
	frappe.require('/assets/js/maia-account.min.js', () => {
		maia.customer_account = new maia.DokosCustomerAccount(wrapper);
	});
}