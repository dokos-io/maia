frappe.listview_settings['Midwife Appointment'] = {
    filters: [["docstatus","!=", "2"], ["date",">=",get_today()]]
};
