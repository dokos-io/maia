frappe.listview_settings['Midwife Appointment'] = {
    filters: [["docstatus","!=", "cancelled"], ["date",">=",get_today()]]
};
