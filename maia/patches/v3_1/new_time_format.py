import frappe

def execute():
    settings = frappe.get_single("System Settings")
    settings.time_format = "HH:mm"
    settings.save()