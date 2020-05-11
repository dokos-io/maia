import frappe
import os

def execute():
	frappe.reload_doc("maia_accounting", "doctype", "accounting_item")
	path = os.path.join(frappe.get_module_path('maia_accounting'), "doctype", "accounting_item", "plan_comptable.json")
	pc = frappe.get_file_json(path)
	for p in pc:
		if not frappe.db.exists("Accounting Item", p):
			doc = frappe.new_doc("Accounting Item")
			doc.accounting_item = p
			doc.update(pc[p])
			doc.insert(ignore_permissions=True)