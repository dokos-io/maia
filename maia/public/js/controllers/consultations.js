// Copyright (c) 2018, DOKOS and contributors
// For license information, please see license.txt
frappe.provide("maia");

frappe.ui.form.on(this.frm.doctype, {

	onload(frm) {
		if (frm.doc.docstatus != 1) {
			get_patient_value(frm);
			refresh_without_codification_price(frm);

			frappe.call({
				"method": "maia.client.get_practitioner",
				args: {
					doctype: "Professional Information Card",
					filters: {
						user: frappe.session.user
					},
					fieldname: "name"
				},
				cache: false,
				callback: function(data) {
					if (!data.exe && data.message) {
						frappe.model.set_value(frm.doctype, frm.docname, "practitioner", data.message.name)
					}
				}
			}),

			frappe.call({
				"method": "frappe.client.get",
				args: {
					doctype: "Codification",
					name: "HN"
				},
				cache: false,
				callback: function(data) {
					if (data.message) {
						frappe.model.set_value(frm.doctype, frm.docname, "without_codification_description", data.message.codification_description)
					}
				}
			})
		}
	},

	refresh(frm) {
		if (frm.doc.docstatus != 1) {
			refresh_total_price(frm);
			refresh_patient_price(frm);
		}
		if (frm.doc.docstatus == 0&&!frm.doc.__islocal) {
			frm.add_custom_button(__('Delete this draft'), function() {
				frappe.confirm(__("Permanently delete {0}?", [frm.doc.name]), function() {
					return frappe.call({
						method: 'maia.utilities.utils.delete_draft_consultation',
						args: {
							doctype: frm.doc.doctype,
							name: frm.doc.name
						},
						callback: function(r, rt) {
							if(!r.exc) {
								frappe.utils.play_sound("delete");
								frappe.model.clear_doc(frm.doc.doctype, frm.doc.name);
								window.history.back();
							}
						}
					})
				})
			});
		}
	},

	paid_immediately(frm) {
		if (frm.doc.paid_immediately == 1) {
			frm.set_df_property('mode_of_payment', 'reqd', 1);
			frm.set_df_property('reference', 'reqd', 1);
		} else {
			frm.set_df_property('mode_of_payment', 'reqd', 0);
			frm.set_df_property('reference', 'reqd', 0);
		}
	},

	lab_exam_template(frm) {
		if(frm.doc.lab_exam_template) {
			frappe.call({
				"method": "maia.maia.doctype.lab_exam_template.lab_exam_template.get_lab_exam_template",
				args: {
					lab_exam_template: frm.doc.lab_exam_template
				},
				callback: function (data) {
						$.each(data.message || [], function(i, v){
							let d = frappe.model.add_child(frm.doc, "Lab Exam Prescription", "lab_prescription_table");
							d.lab_exam = v.exam_type;
							d.additional_notes = v.additional_notes;
						});
						refresh_field("lab_prescription_table");
				}
			});
		}
	},

	drug_list_template(frm) {
		if(frm.doc.drug_list_template) {
			frappe.call({
				"method": "maia.maia.doctype.drug_list_template.drug_list_template.get_drug_list_template",
				args: {
					drug_list_template: frm.doc.drug_list_template
				},
				callback: function (data) {
						$.each(data.message || [], function(i, v){
							let d = frappe.model.add_child(frm.doc, "Drug Prescription", "drug_prescription_table");
							d.drug = v.drug;
							d.posology = v.posology;
							d.pharmaceutical_form = v.pharmaceutical_form;
							d.treatment_duration = v.treatment_duration;
							d.additional_notes = v.additional_notes;
						});
						refresh_field("drug_prescription_table");
				}
			});
		}
	},

	hundred_percent_maternity(frm) {
		frm.doc.hundred_percent_maternity === 1 && frm.set_value("malady", 0);
		refresh_codification_price(frm);
	},

	malady(frm) {
		frm.doc.malady === 1 && frm.set_value("hundred_percent_maternity", 0);
		refresh_codification_price(frm);
	},

	normal_rate(frm) {
		frm.doc.normal_rate === 1 && frm.set_value("alsace_moselle_rate", 0);
		refresh_codification_price(frm);
	},

	alsace_moselle_rate(frm) {
		frm.doc.alsace_moselle_rate === 1 && frm.set_value("normal_rate", 0);
		refresh_codification_price(frm);
	},

	third_party_payment(frm) {
		refresh_codification_price(frm);
	},

	codification(frm) {
		refresh_codification_price(frm);
		refresh_codification_description(frm);
	},

	lump_sum_travel_allowance(frm) {
		if (frm.doc.lump_sum_travel_allowance) {
			get_codification_list("lump_sum_travel_allowance")
			.then(data => {
				if (data.message == undefined) {
					frappe.msgprint(__("No codification is assigned to this specific allowance type. Please select one codification for this allowance type."))
					lump_sum_allowance_not_selected(frm);
				} else if (data.message.length > 1) {
					frappe.msgprint(multiple_codes_msg)
				} else if (data.message) {

					const lump_sum_travel_allowance = data.message[0].basic_price;

					frappe.model.set_value(frm.doctype, frm.docname, "lump_sum_travel_allowance_codification", data.message[0].name)
					frappe.model.set_value(frm.doctype, frm.docname, "lump_sum_travel_allowance_value", lump_sum_travel_allowance)
					frappe.model.set_value(frm.doctype, frm.docname, "lump_sum_travel_allowance_display", data.message[0].codification + " :  " + format_currency(lump_sum_travel_allowance, frm.doc.currency))
					refresh_total_price(frm);
					refresh_patient_price(frm);
				}
			})
		} else {
			lump_sum_allowance_not_selected(frm);
		}
	},

	night_work_allowance(frm) {
		if (frm.doc.night_work_allowance == 0) {
			night_work_allowance_not_selected(frm);
		} else {
			night_work_calculation(frm);
		}
	},

	night_work_allowance_type(frm) {
		night_work_calculation(frm);
	},

	mileage_allowance(frm) {
		if (frm.doc.mileage_allowance == 0) {
			mileage_allowance_not_selected(frm);
		} else {
			mileage_allowance_calculation(frm);
		}
	},

	mileage_allowance_type(frm) {
		mileage_allowance_calculation(frm);
	},

	number_of_kilometers(frm) {
		mileage_allowance_calculation(frm);
	},

	sundays_holidays_allowance(frm) {
		if (frm.doc.sundays_holidays_allowance) {
			get_codification_list("sundays_holidays_allowance")
			.then(data => {
				if (data.message == undefined) {
					frappe.msgprint(no_data_msg)
					sundays_holidays_allowance_not_selected(frm);
				} else if (data.message.length > 1) {
					frappe.msgprint(multiple_codes_msg)
				} else if (data.message) {

					const sundays_holidays_price = data.message[0].basic_price;

					frappe.model.set_value(frm.doctype, frm.docname, "sundays_holidays_allowance_codification", data.message[0].name)
					frappe.model.set_value(frm.doctype, frm.docname, "sundays_holidays_allowance_value", sundays_holidays_price)
					frappe.model.set_value(frm.doctype, frm.docname, "sundays_holidays_allowance_display", data.message[0].codification + " :  " + format_currency(sundays_holidays_price, frm.doc.currency))
					refresh_total_price(frm);
					refresh_patient_price(frm);
				}
			})
		} else {
			sundays_holidays_allowance_not_selected(frm);
		}
	},

	without_codification(frm) {
		refresh_without_codification_price(frm);
	}
});

const refresh_codification_price = (frm) => {
	if (frm.doc.codification.length) {
		getCodification(frm.doc.codification)
		.then(r => {
			const result = r.reduce((acc, d) => {
				const acc_price = (frm.doc.third_party_payment == 1) ? format_currency(acc.basic_price, frm.doc.currency) :
					format_currency(acc.billing_price, frm.doc.currency);
				const d_price = (frm.doc.third_party_payment == 1) ? format_currency(d.basic_price, frm.doc.currency) :
					format_currency(d.billing_price, frm.doc.currency);

				let newObj = {...acc};
				newObj.basic_price = acc.basic_price + d.basic_price;
				newObj.billing_price = acc.billing_price + d.billing_price;
				newObj.codification = acc.codification + `<br> ${d.codification}`;
				newObj.codification_display = acc.hasOwnProperty("codification_display") ? acc.codification_display + `<br> ${d.codification}: ${d_price}` :
					`${acc.codification}: ${acc_price}<br> ${d.codification}: ${d_price}`;

				return newObj;
			})
			if (!result.hasOwnProperty("codification_display")) {
				const price = (frm.doc.third_party_payment == 1) ? format_currency(result.basic_price, frm.doc.currency) :
					format_currency(result.billing_price, frm.doc.currency);
				result.codification_display = `${result.codification}: ${price}`;
			}
			return result;
		})
		.then((conso) => refresh_codification_price_split(frm, conso))
	} else {
		frappe.model.set_value(frm.doctype, frm.docname, "codification_value", 0);
		frappe.model.set_value(frm.doctype, frm.docname, "overpayment_value", 0);
		frappe.model.set_value(frm.doctype, frm.docname, "codification_display", "");
		frappe.model.set_value(frm.doctype, frm.docname, "cpam_share_display", "");
		frappe.model.set_value(frm.doctype, frm.docname, "overpayment_display", "");
		refresh_total_price(frm);
		refresh_patient_price(frm);
	}
};

const get_reimbursable_price = frm => {
	return flt(frm.doc.codification_value + frm.doc.lump_sum_travel_allowance_value + frm.doc.mileage_allowance_value +
		frm.doc.night_work_allowance_value + frm.doc.sundays_holidays_allowance_value)
}

const refresh_codification_price_split = (frm, data) => {
	let codification_price =  data.billing_price;
	let overpayment = 0;
	let cpam_price = 0;

	if (frm.doc.third_party_payment == 1) {
		codification_price = data.basic_price;
		overpayment = data.billing_price - data.basic_price;
	}

	frappe.model.set_value(frm.doctype, frm.docname, "overpayment_value", overpayment);
	frappe.model.set_value(frm.doctype, frm.docname, "overpayment_display", overpayment > 0 ? format_currency(overpayment, frm.doc.currency) : "");

	frappe.model.set_value(frm.doctype, frm.docname, "codification_value", codification_price);
	frappe.model.set_value(frm.doctype, frm.docname, "codification_display", data.codification_display);

	if ((frm.doc.third_party_payment == 1) && (frm.doc.hundred_percent_maternity == 1)) {
		cpam_price = get_reimbursable_price(frm);
	}

	if ((frm.doc.third_party_payment == 1) && (frm.doc.malady == 1) && (frm.doc.normal_rate == 1)) {
		cpam_price = get_reimbursable_price(frm) * 0.7;
	}

	if ((frm.doc.third_party_payment == 1) && (frm.doc.malady == 1) && (frm.doc.alsace_moselle_rate == 1)) {
		cpam_price =  get_reimbursable_price(frm) * 0.9;
	}

	frappe.model.set_value(frm.doctype, frm.docname, "cpam_share_display", format_currency(cpam_price, frm.doc.currency));
	refresh_total_price(frm);
	refresh_patient_price(frm);
};

const refresh_codification_description = (frm) => {
	let codification_description = "";
	if (frm.doc.codification) {
		getCodification(frm.doc.codification)
		.then(r => {
			r.forEach(codif => {
				codification_description += `${codif.codification_description} <br>`;
			})
		})
		.then(() => set_codification_description(frm, codification_description))
	} else {
		set_codification_description(frm, codification_description);
	}
}

const set_codification_description = (frm, description) => {
	frappe.model.set_value(frm.doctype, frm.docname, "codification_description", description);
}

async function getCodification(codifications) {
	let result = []
	for (let i = 0; i < codifications.length; i++) {
		const values = await frappe.call({
			"method": "frappe.client.get",
			args: {
				doctype: "Codification",
				name: codifications[i].codification
			},
			cache: false,
			callback: function(data) {
				return data;
			}
		});
		result.push(values.message);
	}
	return result;
}

async function get_codification_list(filterName) {
	
	const result = await frappe.call({
		"method": "frappe.client.get_list",
		args: {
			doctype: "Codification",
			fields: ["name", "codification", "basic_price", "billing_price"],
			filters: {
				[filterName]: 1
			}
		},
		cache: false,
		callback: function(data) {
			return data.message;
		},
		error: function(frm) {
			frappe.throw(error_msg);
		}
	})
	return result;
}

const refresh_without_codification_price = (frm) => {
	frappe.model.set_value(frm.doctype, frm.docname, "without_codification_display", "HN :  " + format_currency(frm.doc.without_codification, frm.doc.currency))
	refresh_total_price(frm);
	refresh_patient_price(frm);
}

const sundays_holidays_allowance_not_selected = (frm) => {
	const sundays_holidays_price = 0;
	frappe.model.set_value(frm.doctype, frm.docname, "sundays_holidays_allowance_codification", "")
	frappe.model.set_value(frm.doctype, frm.docname, "sundays_holidays_allowance_value", sundays_holidays_price)
	frappe.model.set_value(frm.doctype, frm.docname, "sundays_holidays_allowance_display", "")
	refresh_total_price(frm);
	refresh_patient_price(frm);
}

const lump_sum_allowance_not_selected = (frm) => {
	const lump_sum_travel_allowance = 0;
	frappe.model.set_value(frm.doctype, frm.docname, "lump_sum_travel_allowance_codification", "")
	frappe.model.set_value(frm.doctype, frm.docname, "lump_sum_travel_allowance_value", lump_sum_travel_allowance)
	frappe.model.set_value(frm.doctype, frm.docname, "lump_sum_travel_allowance_display", "")
	refresh_total_price(frm);
	refresh_patient_price(frm);
}

const night_work_allowance_not_selected = (frm) => {
	const night_work_allowance_price = 0;
	frappe.model.set_value(frm.doctype, frm.docname, "night_work_allowance_codification", "")
	frappe.model.set_value(frm.doctype, frm.docname, "night_work_allowance_value", night_work_allowance_price)
	frappe.model.set_value(frm.doctype, frm.docname, "night_work_allowance_display", "")
	refresh_total_price(frm);
	refresh_patient_price(frm);
}

const night_work_calculation = (frm) => {
	const filterName = (frm.doc.night_work_allowance_type == "20h-0h | 6h-8h") ? "night_work_allowance_1" : "night_work_allowance_2";
	get_codification_list(filterName)
	.then(data => {
		if (data.message == undefined) {
			frappe.msgprint(__("No codification is assigned to this specific allowance type. Please select one codification for this allowance type."))
			night_work_allowance_not_selected(frm);
		} else if (data.message.length > 1) {
			frappe.msgprint(multiple_codes_msg)
		} else if (data.message) {
	
			const night_work_allowance_price = data.message[0].basic_price;
	
			frappe.model.set_value(frm.doctype, frm.docname, "night_work_allowance_codification", data.message[0].name)
			frappe.model.set_value(frm.doctype, frm.docname, "night_work_allowance_value", night_work_allowance_price)
			frappe.model.set_value(frm.doctype, frm.docname, "night_work_allowance_display", data.message[0].codification + " :  " + format_currency(night_work_allowance_price, frm.doc.currency))
			refresh_total_price(frm);
			refresh_patient_price(frm);
		}
	})
}

let mileage_allowance_not_selected = function(frm) {
	const mileage_allowance_price = 0;
	frappe.model.set_value(frm.doctype, frm.docname, "mileage_allowance_codification", "")
	frappe.model.set_value(frm.doctype, frm.docname, "mileage_allowance_value", mileage_allowance_price)
	frappe.model.set_value(frm.doctype, frm.docname, "mileage_allowance_display", "")
	refresh_total_price(frm);
	refresh_patient_price(frm);
}

let mileage_allowance_calculation = function(frm) {
	const filterName = (frm.doc.mileage_allowance_type == "Lowland") ? "mileage_allowance_lowland" : 
		((frm.doc.mileage_allowance_type == "Mountain") ? "mileage_allowance_mountain" : "mileage_allowance_walking_skiing")
	get_codification_list(filterName)
	.then(data => {
		if (data.message == undefined) {
			frappe.msgprint(no_data_msg)
			mileage_allowance_not_selected(frm);
		} else if (data.message.length > 1) {
			frappe.msgprint(multiple_codes_msg)
		} else if (data.message) {

			const mileage_allowance_price = data.message[0].basic_price * (frm.doc.number_of_kilometers || 0);

			frappe.model.set_value(frm.doctype, frm.docname, "mileage_allowance_codification", data.message[0].name)
			frappe.model.set_value(frm.doctype, frm.docname, "mileage_allowance_value", mileage_allowance_price)
			frappe.model.set_value(frm.doctype, frm.docname, "mileage_allowance_display", data.message[0].codification + " :  " + format_currency(mileage_allowance_price, frm.doc.currency))
			refresh_total_price(frm);
			refresh_patient_price(frm);
		}
	})
};

const refresh_patient_price = (frm) => {
	let patient_price = 0;
	if (frm.doc.third_party_payment == 1) {
		patient_price = (flt(frm.doc.without_codification) || 0) + flt(frm.doc.overpayment_value || 0)

		if ((frm.doc.malady == 1) && (frm.doc.normal_rate == 1)) {
			patient_price += get_reimbursable_price(frm) * 0.3
		} else if ((frm.doc.malady == 1) && (frm.doc.alsace_moselle_rate == 1)) {
			patient_price += get_reimbursable_price(frm) * 0.1
		}
	} else {
		patient_price = flt(frm.doc.total_price)
	}

	frappe.model.set_value(frm.doctype, frm.docname, "patient_price", patient_price)
}

const refresh_total_price = (frm) => {

	let total_price = 0;
	const fields = ["codification_value", "overpayment_value", "sundays_holidays_allowance_value", "lump_sum_travel_allowance_value", 
		"night_work_allowance_value", "mileage_allowance_value", "without_codification"]

	fields.forEach(field => {
		total_price += flt(frm.doc[field]) || 0;
	})

	frappe.model.set_value(frm.doctype, frm.docname, "total_price", total_price)
}

const error_msg = __("You have no codification setup for this allowance type. Please create a codification for this specific allowance type in the codification list.")
const no_data_msg = __("No codification is assigned to this specific allowance type. Please select one codification for this allowance type.")
const multiple_codes_msg = __("Several codifications exist for this specific allowance. Please check your codifications and select only one.")

const get_patient_value = (frm) => {
	if (!frm.doc.patient) {
		let patient;
		if (frm.doc.pregnancy_folder) {
			patient = frappe.model.get_value('Pregnancy', frm.doc.pregnancy_folder, 'patient');
			frappe.model.set_value(frm.doctype, frm.docname, 'patient', patient);

		} else if (frm.doc.perineum_rehabilitation_folder) {
			patient = frappe.model.get_value('Perineum Rehabilitation', frm.doc.perineum_rehabilitation_folder, 'patient');
			frappe.model.set_value(frm.doctype, frm.docname, 'patient', patient);

		} else if (frm.doc.prenatal_interview_folder) {
			patient = frappe.model.get_value('Prenatal Interview', frm.doc.prenatal_interview_folder, 'patient');
			frappe.model.set_value(frm.doctype, frm.docname, 'patient', patient);

		} else if (frm.doc.gynecological_folder) {
			patient = frappe.model.get_value('Gynecology', frm.doc.gynecological_folder, 'patient');
			frappe.model.set_value(frm.doctype, frm.docname, 'patient', patient);
		}
	}
}

{% include "maia/public/js/controllers/print_settings.js" %}
