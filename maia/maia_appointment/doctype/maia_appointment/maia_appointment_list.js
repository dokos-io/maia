frappe.listview_settings['Midwife Appointment'] = {
    filters: [["docstatus","!=", "2"], ["date",">=",frappe.datetime.get_today()]]
};
