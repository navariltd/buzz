# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AttendeeRegistration(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from buzz.events.doctype.event_attendee_registration.event_attendee_registration import EventAttendeeRegistration
		from frappe.types import DF

		end_date: DF.Date | None
		end_time: DF.Time | None
		event: DF.Link
		event_attendees: DF.Table[EventAttendeeRegistration]
		event_name: DF.Data | None
		name: DF.Int | None
		start_date: DF.Date | None
		start_time: DF.Time | None
	# end: auto-generated types
	
