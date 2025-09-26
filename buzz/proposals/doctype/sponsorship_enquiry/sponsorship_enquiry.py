# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from buzz.payments import mark_payment_as_received


class SponsorshipEnquiry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		company_logo: DF.AttachImage
		company_name: DF.Data
		event: DF.Link
		status: DF.Literal["Approval Pending", "Payment Pending", "Paid", "Withdrawn"]
		tier: DF.Link | None
	# end: auto-generated types

	def on_payment_authorized(self, payment_status: str):
		if payment_status in ("Authorized", "Completed"):
			mark_payment_as_received(self.doctype, self.name)
			frappe.get_doc(
				{
					"doctype": "Event Sponsor",
					"company_name": self.company_name,
					"company_logo": self.company_logo,
					"event": self.event,
					"tier": self.tier,
					"enquiry": self.name,
				}
			).insert(ignore_permissions=True)
			self.db_set("status", "Paid")
