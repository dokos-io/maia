import frappe

def execute():
    for dt in ["Payment", "Revenue", "Expense"]:
        docs = frappe.get_all(dt, filters={"docstatus": 2, "status": ("!=", "Cancelled")})
        for doc in docs:
            frappe.db.set_value(dt, doc.name, "status", "Cancelled", update_modified=False)