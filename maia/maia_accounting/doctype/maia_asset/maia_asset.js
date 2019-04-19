// Copyright (c) 2019, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Maia Asset', {
	refresh(frm) {
		add_expense_btn(frm);

		if (frm.doc.docstatus == 1) {
			frm.trigger("setup_chart");
		}
	},
	depreciation_duration(frm) {
		set_rate(frm);
	},
	depreciation_rate(frm) {
		set_duration(frm);
		calculate_depreciations(frm);
	},
	setup_chart(frm) {
		const x_intervals = [frm.doc.acquisition_date];
		const asset_values = [frm.doc.asset_value];

		$.each(frm.doc.asset_depreciations || [], function(i, v) {
			x_intervals.push(v.depreciation_date);
			asset_values.push(flt(v.depreciation_base) - flt(v.depreciation_amount))
		});

		frm.dashboard.render_graph({
			title: __("Asset Value"),
			data: {
				labels: x_intervals,
				datasets: [{
					values: asset_values,
				}]
			},
			lineOptions: {
				regionFill: 1
			},
			tooltipOptions: {
				formatTooltipY: d => d.toFixed(2) + ' €'
			}
		});
	}
});

const add_expense_btn = frm => {
	if (frm.doc.docstatus == 1 && !frm.doc.expense) {
		frm.set_intro(__("No expense has been registered against this asset. Click on 'Actions > Expense' to register it."))
		frm.page.add_action_item(__('Purchase the asset'), function() {
			make_expense(frm);
		})
	}
}

const add_revenue_btn = frm => {
	if (frm.doc.docstatus == 1 && !frm.doc.expense) {
		frm.page.add_action_item(__('Sell the asset'), function() {
			make_revenue(frm);
		})
	}
}

const make_expense = frm => {
	frappe.xcall('maia.maia_accounting.doctype.expense.expense.get_asset_expense', {dt: frm.doctype, dn: frm.docname})
	.then(e => {
		if (e) {
			const doclist = frappe.model.sync(e);
			frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
		}
	})
}

const make_revenue = frm => {
	frappe.xcall('maia.maia_accounting.doctype.revenue.revenue.get_asset_revenue', {dt: frm.doctype, dn: frm.docname})
	.then(e => {
		if (e) {
			const doclist = frappe.model.sync(e);
			frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
		}
	})
}

const set_duration = frm => {
	if (frm.doc.depreciation_rate) {
		frm.set_value("depreciation_duration", Math.ceil(100 / frm.doc.depreciation_rate));
	}
}

const set_rate = frm => {
	if (frm.doc.depreciation_duration) {
		frm.set_value("depreciation_rate", (100 / frm.doc.depreciation_duration));
	}
}

const calculate_depreciations = frm => {
	frm.set_value("asset_depreciations", []);
	if (frm.doc.depreciation_rate && frm.doc.depreciation_duration) {
		frappe.xcall("maia.maia_accounting.doctype.maia_asset.maia_asset.get_depreciation_schedule", {doc: frm.doc})
		.then(e => {
			if(e) {
				e.forEach(value => {
					let row = frappe.model.add_child(frm.doc, "Maia Asset Depreciation", "asset_depreciations");
					row.depreciation_date = value.depreciation_date;
					row.depreciation_base = value.depreciation_base;
					row.depreciation_amount = value.depreciation_amount;
					row.cumulated_depreciation = value.cumulated_depreciation;
					row.deductible_amount = frm.doc.professional_percentage * value.depreciation_amount;
					row.non_deductible_amount = (1 - frm.doc.professional_percentage) * value.depreciation_amount;
				})
				frm.refresh_fields();
			}
		})

	}
}