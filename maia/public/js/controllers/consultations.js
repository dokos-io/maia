// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt
    
frappe.ui.form.on(this.frm.doctype, {

    onload: function(frm) {
	get_patient_value(frm);
	refresh_codification_price(frm);
	refresh_without_codification_price(frm);
    }

});


frappe.ui.form.on(this.frm.doctype, "third_party_payment", function(frm) {
    refresh_codification_price(frm);
});

frappe.ui.form.on(this.frm.doctype, "codification", function(frm) {
    refresh_codification_price(frm);
});

var refresh_codification_price = function(frm) {
    if (frm.doc.codification) {
	    frappe.call({
		"method": "frappe.client.get",
		args: {
		    doctype: "Codification",
		    name: frm.doc.codification
		},
		cache: false,
		callback: function (data) {
		    if (data.message) {
			if (frm.doc.third_party_payment==1) {
			    codification_price = data.message.basic_price;
			} else {
			    codification_price = data.message.billing_price;
			}
			frappe.model.set_value(frm.doctype, frm.docname, "codification_value", codification_price)
			frappe.model.set_value(frm.doctype, frm.docname, "codification_display", data.message.codification + " :  " + format_currency(codification_price, frm.doc.currency))
			refresh_total_price(frm);
			refresh_patient_price(frm);
		    }
		}
	    })
	} else {
	    codification_price = 0;
	    frappe.model.set_value(frm.doctype, frm.docname, "codification_value", codification_price)
	    frappe.model.set_value(frm.doctype, frm.docname, "codification_display", "")
	    refresh_total_price(frm);
	    refresh_patient_price(frm);
	}
};

frappe.ui.form.on(this.frm.doctype, "without_codification", function(frm) {
    refresh_without_codification_price(frm);
});

var refresh_without_codification_price = function(frm) {
    frappe.model.set_value(frm.doctype, frm.docname, "without_codification_display", "HN :  " + format_currency(frm.doc.without_codification, frm.doc.currency))
    refresh_total_price(frm);
    refresh_patient_price(frm);
}

frappe.ui.form.on(this.frm.doctype, "sundays_holidays_allowance", function(frm) {
	if (frm.doc.sundays_holidays_allowance) {
	    frappe.call({
		"method": "frappe.client.get_list",
		args: {
		    doctype: "Codification",
		    fields: ["name", "codification", "basic_price", "billing_price"],
		    filters: {"sundays_holidays_allowance": 1}
		},
		cache: false,
		callback: function (data) {
		    if (data.message == undefined) {
			msgprint(no_data_msg)
			sundays_holidays_allowance_not_selected(frm);
		    } else if (data.message.length > 1) {
			msgprint(multiple_codes_msg)
		    } else if (data.message) {
			
			sundays_holidays_price = data.message[0].basic_price;
			
			frappe.model.set_value(frm.doctype, frm.docname, "sundays_holidays_allowance_codification", data.message[0].name)
			frappe.model.set_value(frm.doctype, frm.docname, "sundays_holidays_allowance_value", sundays_holidays_price)
			frappe.model.set_value(frm.doctype, frm.docname, "sundays_holidays_allowance_display", data.message[0].codification + " :  " + format_currency(sundays_holidays_price, frm.doc.currency))
			refresh_total_price(frm);
			refresh_patient_price(frm);
		    }
		}
	    })
	} else {
	    sundays_holidays_allowance_not_selected(frm);
	}
    
});

var sundays_holidays_allowance_not_selected = function(frm) {
    sundays_holidays_price = 0;
    frappe.model.set_value(frm.doctype, frm.docname, "sundays_holidays_allowance_codification", "")
    frappe.model.set_value(frm.doctype, frm.docname, "sundays_holidays_allowance_value", sundays_holidays_price)
    frappe.model.set_value(frm.doctype, frm.docname, "sundays_holidays_allowance_display", "")
    refresh_total_price(frm);
    refresh_patient_price(frm);
}
		  
frappe.ui.form.on(this.frm.doctype, "lump_sum_travel_allowance", function(frm) {
	if (frm.doc.lump_sum_travel_allowance) {
	    frappe.call({
		"method": "frappe.client.get_list",
		args: {
		    doctype: "Codification",
		    fields: ["name", "codification", "basic_price", "billing_price"],
		    filters: {"lump_sum_travel_allowance": 1}
		},
		cache: false,
		callback: function (data) {
		    if (data.message == undefined) {
			msgprint(__("No codification is assigned to this specific allowance type. Please select one codification for this allowance type."))
			lump_sum_allowance_not_selected(frm);
		    } else if (data.message.length > 1) {
			msgprint(multiple_codes_msg)
		    } else if (data.message) {
			
			lump_sum_travel_allowance = data.message[0].basic_price;
			
			frappe.model.set_value(frm.doctype, frm.docname, "lump_sum_travel_allowance_codification", data.message[0].name)
			frappe.model.set_value(frm.doctype, frm.docname, "lump_sum_travel_allowance_value", lump_sum_travel_allowance)
			frappe.model.set_value(frm.doctype, frm.docname, "lump_sum_travel_allowance_display", data.message[0].codification + " :  " + format_currency(lump_sum_travel_allowance, frm.doc.currency))
			refresh_total_price(frm);
			refresh_patient_price(frm);
		    }
		},
		error: function (frm) {
		    frappe.throw(error_msg);		    
		}
	    })
	} else {
	    lump_sum_allowance_not_selected(frm);
	}
});

var lump_sum_allowance_not_selected = function (frm) {
    lump_sum_travel_allowance = 0;
    frappe.model.set_value(frm.doctype, frm.docname, "lump_sum_travel_allowance_codification", "")
    frappe.model.set_value(frm.doctype, frm.docname, "lump_sum_travel_allowance_value", lump_sum_travel_allowance)
    frappe.model.set_value(frm.doctype, frm.docname, "lump_sum_travel_allowance_display", "")
    refresh_total_price(frm);
    refresh_patient_price(frm);
}

frappe.ui.form.on(this.frm.doctype, "night_work_allowance", function(frm) {
         if (frm.doc.night_work_allowance == 0) {
	     night_work_allowance_not_selected(frm);
	 } else {
	     night_work_calculation(frm);
	 }
});

frappe.ui.form.on(this.frm.doctype, "night_work_allowance_type", function(frm) {
    night_work_calculation(frm);
});

var night_work_allowance_not_selected = function(frm) {
    night_work_allowance_price = 0;
    frappe.model.set_value(frm.doctype, frm.docname, "night_work_allowance_codification", "")
    frappe.model.set_value(frm.doctype, frm.docname, "night_work_allowance_value", night_work_allowance_price)
    frappe.model.set_value(frm.doctype, frm.docname, "night_work_allowance_display", "")
    refresh_total_price(frm);
    refresh_patient_price(frm);
}

var night_work_calculation = function(frm) {
    	 if (frm.doc.night_work_allowance_type == "20h-0h | 6h-8h") {
	    frappe.call({
		"method": "frappe.client.get_list",
		args: {
		    doctype: "Codification",
		    fields: ["name", "codification", "basic_price", "billing_price"],
		    filters: {"night_work_allowance_1": 1}
		},
		cache: false,
		callback: function (data) {
		    if (data.message == undefined) {
			msgprint(__("No codification is assigned to this specific allowance type. Please select one codification for this allowance type."))
			night_work_allowance_not_selected(frm);
		    } else if (data.message.length > 1) {
			msgprint(multiple_codes_msg)
		    } else if (data.message) { 
			
			night_work_allowance_price = data.message[0].basic_price;
			
			frappe.model.set_value(frm.doctype, frm.docname, "night_work_allowance_codification", data.message[0].name)
			frappe.model.set_value(frm.doctype, frm.docname, "night_work_allowance_value", night_work_allowance_price)
			frappe.model.set_value(frm.doctype, frm.docname, "night_work_allowance_display", data.message[0].codification + " :  " + format_currency(night_work_allowance_price, frm.doc.currency))
			refresh_total_price(frm);
			refresh_patient_price(frm);
		    }
		},
		error: function(frm) {
		    frappe.throw(error_msg);
		}
	    })
	} else if (frm.doc.night_work_allowance_type == "0h-6h") {
	    frappe.call({
		"method": "frappe.client.get_list",
		args: {
		    doctype: "Codification",
		    fields: ["name", "codification", "basic_price", "billing_price"],
		    filters: {"night_work_allowance_2": 1}
		},
		cache: false,
		callback: function (data) {
		    if (data.message == undefined) {
			msgprint(no_data_msg)
			night_work_allowance_not_selected(frm);
		    } else if (data.message.length > 1) {
			msgprint(multiple_codes_msg)
		    } else if (data.message) {

			night_work_allowance_price = data.message[0].basic_price;
			
			frappe.model.set_value(frm.doctype, frm.docname, "night_work_allowance_codification", data.message[0].name)
			frappe.model.set_value(frm.doctype, frm.docname, "night_work_allowance_value", night_work_allowance_price)
			frappe.model.set_value(frm.doctype, frm.docname, "night_work_allowance_display", data.message[0].codification + " :  " + format_currency(night_work_allowance_price, frm.doc.currency))
			refresh_total_price(frm);
			refresh_patient_price(frm);
		    }
		},
		error: function(frm) {
		    frappe.throw(error_msg);
		}
	    })
	}


}

frappe.ui.form.on(this.frm.doctype, "mileage_allowance", function(frm) {
         if (frm.doc.mileage_allowance == 0) {
	     mileage_allowance_not_selected(frm);
	 } else {
	     mileage_allowance_calculation(frm);
	 }
});

frappe.ui.form.on(this.frm.doctype, "mileage_allowance_type", function(frm) {
    mileage_allowance_calculation(frm);
});

frappe.ui.form.on(this.frm.doctype, "number_of_kilometers", function(frm) {
    mileage_allowance_calculation(frm);
});

var mileage_allowance_not_selected = function(frm) {
    mileage_allowance_price = 0;
    frappe.model.set_value(frm.doctype, frm.docname, "mileage_allowance_codification", "")
    frappe.model.set_value(frm.doctype, frm.docname, "mileage_allowance_value", mileage_allowance_price)
    frappe.model.set_value(frm.doctype, frm.docname, "mileage_allowance_display", "")
    refresh_total_price(frm);
    refresh_patient_price(frm);
}

var mileage_allowance_calculation = function(frm) {
    if (frm.doc.mileage_allowance_type == "Lowland") {
	    frappe.call({
		"method": "frappe.client.get_list",
		args: {
		    doctype: "Codification",
		    fields: ["name", "codification", "basic_price", "billing_price"],
		    filters: {"mileage_allowance_lowland": 1}
		},
		cache: false,
		callback: function (data) {
		    if (data.message == undefined) {
			msgprint(no_data_msg)
			mileage_allowance_not_selected(frm);
		    } else if (data.message.length > 1) {
			msgprint(multiple_codes_msg)
		    } else if (data.message) {
			
			mileage_allowance_price = data.message[0].basic_price * frm.doc.number_of_kilometers;
			
			frappe.model.set_value(frm.doctype, frm.docname, "mileage_allowance_codification", data.message[0].name)
			frappe.model.set_value(frm.doctype, frm.docname, "mileage_allowance_value", mileage_allowance_price)
			frappe.model.set_value(frm.doctype, frm.docname, "mileage_allowance_display", data.message[0].codification + " :  " + format_currency(mileage_allowance_price, frm.doc.currency))
			refresh_total_price(frm);
			refresh_patient_price(frm);
		    }
		},
		error: function(frm) {
		    frappe.throw(error_msg);
		}
	    })
	} else if (frm.doc.mileage_allowance_type == "Mountain") {
	    frappe.call({
		"method": "frappe.client.get_list",
		args: {
		    doctype: "Codification",
		    fields: ["name", "codification", "basic_price", "billing_price"],
		    filters: {"mileage_allowance_mountain": 1}
		},
		cache: false,
		callback: function (data) {
		    if (data.message == undefined) {
			msgprint(no_data_msg)
			mileage_allowance_not_selected(frm);
		    } else if (data.message.length > 1) {
			msgprint(mutiple_codes_msg)
		    } else if (data.message) {
			
			mileage_allowance_price = data.message[0].basic_price * frm.doc.number_of_kilometers;
		
			frappe.model.set_value(frm.doctype, frm.docname, "mileage_allowance_codification", data.message[0].name)
			frappe.model.set_value(frm.doctype, frm.docname, "mileage_allowance_value", mileage_allowance_price)
			frappe.model.set_value(frm.doctype, frm.docname, "mileage_allowance_display", data.message[0].codification + " :  "  + format_currency(mileage_allowance_price, frm.doc.currency))
			refresh_total_price(frm);
			refresh_patient_price(frm);
		    }
		},
		error: function(frm) {
		    frappe.throw(error_msg);
		}
	    })
	} else if (frm.doc.mileage_allowance_type == "Walking/Skiing") {
	    frappe.call({
		"method": "frappe.client.get_list",
		args: {
		    doctype: "Codification",
		    fields: ["name", "codification", "basic_price", "billing_price"],
		    filters: {"mileage_allowance_walking_skiing": 1}
		},
		cache: false,
		callback: function (data) {
		    if (data.message == undefined) {
			msgprint(no_data_msg)
			mileage_allowance_not_selected(frm);
		    } else if (data.message.length > 1) {
			msgprint(multiple_codes_msg)
		    } else if (data.message) {

			mileage_allowance_price = data.message[0].basic_price * frm.doc.number_of_kilometers;
			
			frappe.model.set_value(frm.doctype, frm.docname, "mileage_allowance_codification", data.message[0].name)
			frappe.model.set_value(frm.doctype, frm.docname, "mileage_allowance_value", mileage_allowance_price)
			frappe.model.set_value(frm.doctype, frm.docname, "mileage_allowance_display", data.message[0].codification + " :  " + format_currency(mileage_allowance_price, frm.doc.currency))
			refresh_total_price(frm);
			refresh_patient_price(frm);
		    }
		},
		error: function(frm) {
		    frappe.throw(error_msg);
		}
	    })
	}

};


var refresh_patient_price = function (frm) {

    if (frm.doc.third_party_payment == 1) {
	patient_price = frm.doc.without_codification
    } else {
	patient_price = frm.doc.total_price
    }

    frappe.model.set_value(frm.doctype, frm.docname, "patient_price", patient_price)
}

var refresh_total_price = function(frm) {

    total_price = 0;

    if (isNaN(frm.doc.codification_value)) {
    } else {
	total_price += frm.doc.codification_value;
    }

    if (isNaN(frm.doc.sundays_holidays_allowance_value)) {
    } else {
	total_price += frm.doc.sundays_holidays_allowance_value;
    }

    if (isNaN(frm.doc.lump_sum_travel_allowance_value)) {
    } else {
	total_price += frm.doc.lump_sum_travel_allowance_value;
    }

    if (isNaN(frm.doc.night_work_allowance_value)) {
    } else {
	total_price += frm.doc.night_work_allowance_value;
    }

    if (isNaN(frm.doc.mileage_allowance_value)) {
    } else {
	total_price += frm.doc.mileage_allowance_value;
    }

    if (isNaN(frm.doc.without_codification)) {
    } else {
	total_price += frm.doc.without_codification;
    }
    	 
    frappe.model.set_value(frm.doctype, frm.docname, "total_price", total_price)
}

var error_msg = __("You have no codification setup for this allowance type. Please create a codification for this specific allowance type in the codification list.")

var no_data_msg = __("No codification is assigned to this specific allowance type. Please select one codification for this allowance type.")

var multiple_codes_msg = __("Several codifications exist for this specific allowance. Please check your codifications and select only one.")

var get_patient_value = function(frm) {

    if (!frm.doc.patient) {
    
	if (frm.doc.pregnancy_folder) {
	    patient = frappe.model.get_value ('Pregnancy', frm.doc.pregnancy_folder, 'patient');
	    frappe.model.set_value(frm.doctype, frm.docname, 'patient', patient);

	} else if (frm.doc.perineum_rehabilitation_folder) {
	    patient = frappe.model.get_value ('Perineum Rehabilitation', frm.doc.perineum_rehabilitation_folder, 'patient');
	    frappe.model.set_value(frm.doctype, frm.docname, 'patient', patient);
	
	} else if (frm.doc.prenatal_interview_folder) {
	    patient = frappe.model.get_value ('Prenatal Interview', frm.doc.prenatal_interview_folder, 'patient');
	    frappe.model.set_value(frm.doctype, frm.docname, 'patient', patient);
	
	} else if (frm.doc.gynecological_folder) {
	    patient = frappe.model.get_value ('Gynecology', frm.doc.gynecological_folder, 'patient');
	    frappe.model.set_value(frm.doctype, frm.docname, 'patient', patient);
	}
    }
}
