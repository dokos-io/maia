// Copyright (c) 2016, DOKOS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Fichier des Ecritures Comptables"] = {
	"filters": [
		{
			"fieldname": "practitioner",
			"label": __("Practitioner"),
			"fieldtype": "Link",
			"options": "Professional Information Card",
			"reqd": 1
		},
		{
			"fieldname": "fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Maia Fiscal Year",
			"default": frappe.defaults.get_user_default("fiscal_year"),
			"reqd": 1
		}
	],
	onload: function(query_report) {
		query_report.page.add_inner_button(__("Export"), function() {
			fec_export(query_report);
		});

		query_report.export_report = function() {
			fec_export(query_report);
		};
	}
};

let fec_export = function(query_report) {
	const fiscal_year = query_report.get_values().fiscal_year;
	const practitioner = query_report.get_values().practitioner;

	frappe.db.get_value("Professional Information Card", practitioner, "siret_number", (value) => {
		const practitioner_data = value.siret_number.substring(0,8);
		if (practitioner_data === null || practitioner_data === undefined) {
			frappe.msgprint(__("Please register the SIREN number in the professional information card"));
		} else {
			frappe.db.get_value("Maia Fiscal Year", fiscal_year, "year_end_date", (r) => {
				const fy = r.year_end_date;
				const title = practitioner_data + "FEC" + moment(fy).format('YYYYMMDD');
				const column_row = query_report.columns.map(col => col.label);
				const column_data = query_report.get_data_for_csv(false);
				const result = [column_row].concat(column_data);
				downloadify(result, null, title);
			});

		}
	});
};

let downloadify = function(data, roles, title) {
	if (roles && roles.length && !has_common(roles, roles)) {
		frappe.msgprint(__("Export not allowed. You need {0} role to export.", [frappe.utils.comma_or(roles)]));
		return;
	}

	const filename = title + ".txt";
	let csv_data = to_tab_csv(data);
	const a = document.createElement('a');

	if ("download" in a) {
		// Used Blob object, because it can handle large files
		let blob_object = new Blob([csv_data], {
			type: 'text/csv;charset=UTF-8'
		});
		a.href = URL.createObjectURL(blob_object);
		a.download = filename;

	} else {
		// use old method
		a.href = 'data:attachment/csv,' + encodeURIComponent(csv_data);
		a.download = filename;
		a.target = "_blank";
	}

	document.body.appendChild(a);
	a.click();

	document.body.removeChild(a);
};

let to_tab_csv = function(data) {
	let res = [];
	$.each(data, function(i, row) {
		res.push(row.join("\t"));
	});
	return res.join("\n");
};