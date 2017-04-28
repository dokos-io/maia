frappe.listview_settings['Midwife Appointment'] = {
    filters: [["status","!=", "cancelled"], ["date",">=",get_today()]]
};
