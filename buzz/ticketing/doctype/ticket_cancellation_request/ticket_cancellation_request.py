# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class TicketCancellationRequest(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from buzz.ticketing.doctype.ticket_cancellation_item.ticket_cancellation_item import (
			TicketCancellationItem,
		)

		booking: DF.Link
		cancel_full_booking: DF.Check
		tickets: DF.Table[TicketCancellationItem]
	# end: auto-generated types

	pass
