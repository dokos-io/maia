// Copyright (c) 2018, DOKOS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Personal Debit', {
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
			  frm.set_value("personal_debit_account", r.message.personal_debit_account);
			}
		  }
		}),
  
		frm.set_value("transaction_date", frappe.datetime.get_today())
	  frm.set_value("posting_date", frappe.datetime.get_today())
	}
  });