// Copyright (c) 2017, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Cash Deposit', {
    onload: function(frm) {
      frappe.call({
          method: "frappe.client.get",
          args: {
            doctype: "Company",
            name: frm.doc.company,
          },
          callback: function(r, rt) {
            if (r.message) {
              frm.set_value("cash_deposit_account", r.message.default_bank_account);
              frm.set_value("cash_account", r.message.default_cash_account);
              var abbr = r.message.abbr;
              var transfer_account = "58-Virements internes - " + abbr;
              frm.set_value("internal_transfer_account", transfer_account);
            }
          }
        }),

        frm.set_value("transaction_date", frappe.datetime.get_today())
      frm.set_value("posting_date", frappe.datetime.get_today())
    }
});
