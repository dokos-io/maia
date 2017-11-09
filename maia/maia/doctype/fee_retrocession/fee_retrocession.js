// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Fee Retrocession', {
  onload: function(frm) {
    frappe.call({
        method: "frappe.client.get",
        args: {
          doctype: "Company",
          name: frm.doc.company,
        },
        callback: function(r, rt) {
          if (r.message) {
            frm.set_value("bank_account", r.message.default_bank_account);
            frm.set_value("fee_account", r.message.fee_account);
          }
        }
      }),

      frm.set_value("transaction_date", frappe.datetime.get_today())
    frm.set_value("posting_date", frappe.datetime.get_today())
  }
});
