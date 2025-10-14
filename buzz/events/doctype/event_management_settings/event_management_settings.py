# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EventManagementSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		allow_add_ons_change_before_event_start_days: DF.Int
		allow_ticket_cancellation_request_before_event_start_days: DF.Int
		allow_transfer_ticket_before_event_start_days: DF.Int
		apply_gst_on_bookings: DF.Check
		gst_percentage: DF.Percent
		support_email: DF.Data | None
	# end: auto-generated types

	def validate(self):
		"""Validate the settings."""
		self.validate_transfer_days()
		self.set_tax_percentage()

	def set_tax_percentage(self):
		"""Set the GST percentage if applicable."""
		if self.apply_gst_on_bookings and not self.gst_percentage:
			self.gst_percentage = 18

	def validate_transfer_days(self):
		"""Validate that transfer days is a reasonable value."""
		if self.allow_transfer_ticket_before_event_start_days is not None:
			if self.allow_transfer_ticket_before_event_start_days < 0:
				frappe.throw(_("Allow Transfer Ticket Before Event Start Days cannot be negative."))
			elif self.allow_transfer_ticket_before_event_start_days > 365:
				frappe.throw(_("Allow Transfer Ticket Before Event Start Days cannot be more than 365 days."))
