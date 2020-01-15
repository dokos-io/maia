frappe.listview_settings['Maia Appointment'] = {
    filters: [["status","!=", "Cancelled"], ["date",">=",frappe.datetime.get_today()]],
    get_indicator: function(doc) {
		if (doc.status == "Confirmed") {
			return [__("Confirmed"), "green", "status,=,Confirmed"];
		} else if (doc.status == "Cancelled") {
			return [__("Cancelled"), "red", "status,=,Cancelled"];
		} else if (doc.status == "Not confirmed") {
			return [__("Not confirmed"), "orange", "status,=,Not confirmed"];
		}
	}
};
