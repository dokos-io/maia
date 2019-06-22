# Copyright (c) 2019, Dokos and Contributors
# See license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate
from frappe import _

status_map = {
	"Expense": [
		["Draft", "eval:self.docstatus==0"],
		["Paid", "eval:self.outstanding_amount==0 and self.docstatus==1"],
		["Unpaid", "eval:self.outstanding_amount>0 and self.docstatus==1"],
		["Cancelled", "eval:self.docstatus==2"],
	],
	"Revenue": [
		["Draft", "eval:self.docstatus==0"],
		["Paid", "eval:self.outstanding_amount==0 and self.docstatus==1 and self.declared_lost==0"],
		["Unpaid", "eval:self.outstanding_amount>0 and self.docstatus==1 and self.declared_lost==0"],
		["Cancelled", "eval:self.docstatus==2"],
		["Lost", "eval:self.outstanding_amount==0 and self.docstatus==1 and self.declared_lost!=0"]
	],
	"Payment": [
		["Draft", "eval:self.docstatus==0"],
		["Reconciled", "eval:self.clearance_date"],
		["Unreconciled", "eval:self.clearance_date is None"],
		["Cancelled", "eval:self.docstatus==2"]
	],
	"Maia Asset": [
		["Fully depreciated", "is_fully_depreciated"],
		["Partly depreciated", "is_partly_depreciated"],
		["Not depreciated", "is_not_depreciated"]
	]
}

class StatusUpdater(Document):
	def set_status(self, update=False, status=None, update_modified=True):
		if self.is_new():
			if self.get('amended_from'):
				self.status = 'Draft'
			return

		if self.doctype in status_map:
			_status = self.status

			if status and update:
				self.db_set("status", status)

			sl = status_map[self.doctype][:]
			sl.reverse()
			for s in sl:
				if not s[1]:
					self.status = s[0]
					break
				elif s[1].startswith("eval:"):
					if frappe.safe_eval(s[1][5:], None, { "self": self.as_dict(), "getdate": getdate,
							"nowdate": nowdate, "get_value": frappe.db.get_value }):
						self.status = s[0]
						break
				elif getattr(self, s[1])():
					self.status = s[0]
					break

			if self.status != _status and self.status not in ("Cancelled"):
				self.add_comment("Label", _(self.status))

			if update:
				self.db_set('status', self.status, update_modified = update_modified)