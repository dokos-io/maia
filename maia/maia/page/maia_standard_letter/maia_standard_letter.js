frappe.pages['maia-standard-letter'].on_page_load = function(wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Maia Standard Letter'),
		single_column: true
	});

	frappe.maia_standard_letter = new frappe.MaiaStandardLetter(wrapper);
	$(wrapper).bind('show', function() {
		frappe.maia_standard_letter.show();
	});
	frappe.breadcrumbs.add("Maia", "Standard Letter");

	frappe.require('/assets/js/maia-standard-letter.min.js');
}

frappe.MaiaStandardLetter = class MaiaStandardLetter {
	constructor(wrapper) {
		this.wrapper = $(wrapper);
		this.container = this.wrapper.find('.layout-main-section');
		this.container.append($('<div class="standard-letter-container"></div>'));
	}

	show() {

	}
}