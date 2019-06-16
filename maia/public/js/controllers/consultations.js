// Copyright (c) 2018, DOKOS and contributors
// For license information, please see license.txt
frappe.provide("maia");

frappe.ui.form.on(this.frm.doctype, {
	onload(frm) {
		if (frm.doc.docstatus != 1) {
			frappe.db.get_value("Professional Information Card", {user: frappe.session.user}, "name", r => {
				r && frm.set_value("practitioner", data.message.name);
			})

			frappe.db.get_value("Codification", {codification: "HN"}, "codification_description", r => {
				if (r) {
					frm.set_value("without_codification_description", r.codification_description);
				} else {
					frm.msgprint(__("Please add the codification: HN"))
				}
			})
		}
	},

	refresh(frm) {
		show_hide_accounting(frm);
		if (frm.doc.docstatus === 0) {
			new_price_calcultator(frm);
		}
	},

	paid_immediately(frm) {
		frm.set_df_property('mode_of_payment', 'reqd', frm.doc.paid_immediately == 1 ? 1 : 0);
	},

	hundred_percent_maternity(frm) {
		frm.doc.hundred_percent_maternity === 1 ? frm.set_value("malady", 0) : maia.price_calculator.refresh(frm);
	},

	malady(frm) {
		frm.doc.malady === 1 ? frm.set_value("hundred_percent_maternity", 0) : maia.price_calculator.refresh(frm);
	},

	normal_rate(frm) {
		frm.doc.normal_rate === 1 ? frm.set_value("alsace_moselle_rate", 0) : maia.price_calculator.refresh(frm);
	},

	alsace_moselle_rate(frm) {
		frm.doc.alsace_moselle_rate === 1 ? frm.set_value("normal_rate", 0) : maia.price_calculator.refresh(frm);
	},

	third_party_payment(frm) {
		maia.price_calculator.refresh(frm);
	},

	social_security_price(frm) {
		maia.price_calculator.refresh(frm);
	},

	codification(frm) {
		maia.price_calculator.refresh(frm);
		if (frm.doc.codification.length) {
			frm.set_value("codification_description", "")
			frm.doc.codification.forEach(value => {
				frappe.db.get_value("Codification", value.codification, "codification_description", e => {
					frm.set_value("codification_description",
						(frm.doc.codification_description || "") + "<li>" + e.codification_description + "</li>")
				})
			})
		}
	},

	lump_sum_travel_allowance(frm) {
		maia.price_calculator.refresh(frm);
	},

	night_work_allowance(frm) {
		maia.price_calculator.refresh(frm);
	},

	night_work_allowance_type(frm) {
		maia.price_calculator.refresh(frm);
	},

	mileage_allowance(frm) {
		maia.price_calculator.refresh(frm);
	},

	mileage_allowance_type(frm) {
		maia.price_calculator.refresh(frm);
	},

	number_of_kilometers(frm) {
		maia.price_calculator.refresh(frm);
	},

	sundays_holidays_allowance(frm) {
		maia.price_calculator.refresh(frm);
	},

	without_codification(frm) {
		maia.price_calculator.refresh(frm);
	},
	pregnancy_folder: function(frm) {
		if (frm.doc.pregnancy_folder) {
			get_patient_record(frm, "Pregnancy", frm.doc.pregnancy_folder);
		}
	},
	perineum_rehabilitation_folder: function(frm) {
		if (frm.doc.perineum_rehabilitation_folder) {
			get_patient_record(frm, "Perineum Rehabilitation", frm.doc.perineum_rehabilitation_folder);
		}
	},
	prenatal_interview_folder: function(frm) {
		if (frm.doc.prenatal_interview_folder) {
			get_patient_record(frm, "Prenatal Interview", frm.doc.prenatal_interview_folder);
		}
	},
	gynecological_folder: function(frm) {
		if (frm.doc.gynecological_folder) {
			get_patient_record(frm, "Gynecology", frm.doc.gynecological_folder);
		}
	},
	practitioner: function(frm) {
		frm.doc.practitioner&&frappe.db.get_value("Professional Information Card", frm.doc.practitioner, 
			["disable_accounting", "third_party_payment", "social_security_price", "social_security_rate"], e => {
				frappe.run_serially([
					() => frm.set_value("accounting_disabled", e.disable_accounting),
					() => frm.set_value("third_party_payment", e.third_party_payment),
					() => frm.set_value("social_security_price", e.social_security_price),
					() => {
						if (e.social_security_rate == "Normal Rate (70%)" || e.social_security_rate == "") {
							frm.set_value("normal_rate", 1);
						} else if (e.social_security_rate == "Régime d'Alsace-Moselle (90%)") {
							frm.set_value("alsace_moselle_rate", 1);
						}
					}
				])
			})

	},
	accounting_disabled: function(frm) {
		show_hide_accounting(frm);
	}
});

const show_hide_accounting = frm => {
	if (frm.doc.docstatus != 1) {
		frm.toggle_reqd("codification", !frm.doc.accounting_disabled);
	}

	if (frm.doc.accounting_disabled === 1) {
		frm.dashboard.hide();
		frm.dashboard.clear_headline();
		frm.dashboard.set_headline(__("Accounting sections hidden"));
	} else {
		frm.dashboard.show();
		frm.dashboard.clear_headline();
	}
}

const new_price_calcultator = frm => {
	if (!maia.price_calculator) {
		maia.price_calculator = new PriceCalculator(frm);
	}
}

class PriceCalculator {
	constructor(opts) {
		this.frm = opts;
		this.in_progress = false;
		this.calculate_price();
	}

	refresh(frm) {
		this.frm = frm;
		if (!this.in_progress) {
			this.calculate_price();
		} else {
			frappe.timeout(0.5).then(() => { this.calculate_price() })
		}
	}

	async calculate_price() {
		const me = this;
		return await frappe.run_serially([
			() => me.in_progress = true,
			() => me.clear_table(),
			() => me.add_codifications(),
			() => me.add_without_codifications(),
			() => me.add_allowances(),
			() => me.refresh_totals(),
			() => me.in_progress = false
		]);
	}

	clear_table() {
		me.frm.clear_table('consultation_items');
	}

	async add_codifications() {
		const me = this;
		// Codifications
		if (me.frm.doc.codification) {
			return await Promise.all(me.frm.doc.codification.map(value => {
				const calculated_values = me.calculate_values(value.codification, "codification");
				return calculated_values.then(r => {
					me.frm.add_child('consultation_items', r);
					me.frm.refresh_field('consultation_items');
				});
			}));
		}
	}

	async add_without_codifications() {
		const me = this;
		// Without codifications
		if (me.frm.doc.without_codification) {
			const price = me.frm.doc.without_codification;
			const calculated_values = me.calculate_values("HN", "without_codification", price, price, true);
			return await calculated_values.then(r => {
				me.frm.add_child('consultation_items', r);
				me.frm.refresh_field('consultation_items');
			});
		}
	}

	async add_allowances() {
		return await frappe.run_serially([
			() => this.add_sundays_allowance(),
			() => this.add_lump_sum_travel_allowance(),
			() => this.add_night_work_allowance(),
			() => this.add_mileage_allowance()
		])
	}

	async add_sundays_allowance() {
		if (this.frm.doc.sundays_holidays_allowance === 1) {
			return await this.add_allowance("sundays_holidays_allowance");
		}
	}

	async add_lump_sum_travel_allowance() {
		if (this.frm.doc.lump_sum_travel_allowance === 1) {
			return await this.add_allowance("lump_sum_travel_allowance");
		}
	}

	async add_night_work_allowance() {
		if (this.frm.doc.night_work_allowance === 1) {
			const filterName = (this.frm.doc.night_work_allowance_type == "20h-0h | 6h-8h") ? "night_work_allowance_1" : "night_work_allowance_2";
			return await this.add_allowance(filterName);
		}
	}

	async add_mileage_allowance() {
		if (this.frm.doc.mileage_allowance === 1) {
			const filterName = (this.frm.doc.mileage_allowance_type == "Lowland") ? "mileage_allowance_lowland" : 
			((this.frm.doc.mileage_allowance_type == "Mountain") ? "mileage_allowance_mountain" : "mileage_allowance_walking_skiing")
			const km_coef = this.frm.doc.number_of_kilometers || 0;
			return await this.add_allowance(filterName, km_coef);
		}
	}

	async add_allowance(allowance_type, rate_coef=1) {
		return await get_codification_list(allowance_type)
			.then(data => {
				if (data.message == undefined) {
					frappe.msgprint(no_data_msg)
				} else if (data.message.length > 1) {
					frappe.msgprint(multiple_codes_msg)
				} else if (data.message) {
					const basic_price = data.message[0].basic_price * rate_coef;
					const billing_price = data.message[0].billing_price * rate_coef;
					const calculated_values = this.calculate_values(data.message[0].name, "allowance", basic_price, billing_price, true);
					return calculated_values.then(r => {
						this.frm.add_child('consultation_items', r)
						this.frm.refresh_field('consultation_items')
					})
				}
			})
	}

	calculate_values(codification, category, basic_price=0, billing_price=0, force_rate=false) {
		const me = this;
		return new Promise ((resolve) => {
			frappe.db.get_value("Codification", codification, ["name", "codification", "codification_description",
				"basic_price", "billing_price", "accounting_item"], result => {
				if (result) {
					resolve(me.calculate_split(result, category, basic_price, billing_price, force_rate));
				}
			})
		})
	}

	calculate_split(values, category, basic_price=0, billing_price=0, force_rate=false) {
		let obj = {
			"codification_name": values["name"],
			"codification": values["codification"],
			"description": values["codification_description"],
			"rate": force_rate ? billing_price : values["basic_price"],
			"social_security_share": 0,
			"patient_share": force_rate ? billing_price : (this.frm.doc.social_security_price === 1 ? values["basic_price"] : values["billing_price"]),
			"overbilling": 0,
			"category": category
		}

		obj["overbilling"] = this.frm.doc.social_security_price === 1 ? 0 : (force_rate ? (billing_price - basic_price) : (values["billing_price"] - values["basic_price"]))

		if (category !== "without_codification") {
			if ((this.frm.doc.third_party_payment == 1) && (this.frm.doc.hundred_percent_maternity == 1)) {
				obj["rate"] = force_rate ? billing_price : values["basic_price"];
				obj["social_security_share"] = force_rate ? basic_price : values["basic_price"];
				obj["patient_share"] = obj["overbilling"];
			}
		
			if ((this.frm.doc.third_party_payment == 1) && (this.frm.doc.malady == 1) && (this.frm.doc.normal_rate == 1)) {
				obj["rate"] = (this.frm.doc.social_security_price === 1) ? (force_rate ? basic_price : values["basic_price"]): (force_rate ? billing_price : values["basic_price"]);
				obj["social_security_share"] = obj["rate"] * 0.7;
				obj["patient_share"] = obj["rate"] * 0.3 + obj["overbilling"];
			}
		
			if ((this.frm.doc.third_party_payment == 1) && (this.frm.doc.malady == 1) && (this.frm.doc.alsace_moselle_rate == 1)) {
				obj["rate"] = (this.frm.doc.social_security_price === 1) ? (force_rate ? basic_price : values["basic_price"]) : (force_rate ? billing_price : values["basic_price"]);
				obj["social_security_share"] = obj["rate"] * 0.9;
				obj["patient_share"] = obj["rate"] * 0.1 + obj["overbilling"];
			}
		}

		return obj
	}

	refresh_totals() {
		let patient_price = 0;
		let social_security_share=0;
		let total_price = 0;
		let overbilling = 0;
		let without_codification = 0;
		let allowances = 0;
		let codifications = 0;
		this.frm.doc.consultation_items.forEach(value => {
			total_price += value.rate + value.overbilling;
			patient_price += value.patient_share;
			social_security_share += value.social_security_share;
			overbilling += value.overbilling;

			if (value.category == "without_codification") {
				without_codification += value.rate;
			} else if (value.category == "allowance") {
				allowances += value.rate;
			} else if (value.category == "codification") {
				codifications += value.rate;
			}
		})

		this.frm.set_value("codification_value", codifications > 0 ? codifications : 0);
		this.frm.set_value("cpam_share_display", social_security_share > 0 ? social_security_share : 0);
		this.frm.set_value("patient_price", patient_price > 0 ? patient_price : 0);
		this.frm.set_value("total_price", total_price > 0 ? total_price : 0);
		this.frm.set_value("overpayment_value", overbilling > 0 ? overbilling: 0);
		this.frm.set_value("without_codification_display", without_codification > 0 ? without_codification : 0);	
		this.frm.set_value("total_allowances", allowances > 0 ? allowances : 0);
	}

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

const error_msg = __("You have no codification setup for this allowance type. Please create a codification for this specific allowance type in the codification list.")
const no_data_msg = __("No codification is assigned to this specific allowance type. Please select one codification for this allowance type.")
const multiple_codes_msg = __("Several codifications exist for this specific allowance. Please check your codifications and select only one.")

const get_patient_record = (frm, doctype, name) => {
	frappe.db.get_value(doctype, name, "patient_record", e => {
		if (e) {
			frm.set_value("patient_record", e.patient_record);
		}
	})
}

{% include "maia/public/js/controllers/print_settings.js" %}
