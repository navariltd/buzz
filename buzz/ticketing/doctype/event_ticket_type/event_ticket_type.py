# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EventTicketType(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		auto_unpublish_after: DF.Date | None
		company: DF.Data
		currency: DF.Link
		event: DF.Link
		is_published: DF.Check
		linked_item: DF.Link | None
		max_tickets_available: DF.Int
		name: DF.Int | None
		price: DF.Currency
		title: DF.Data
	# end: auto-generated types

	def are_tickets_available(self, num_tickets: int) -> bool:
		if self.remaining_tickets != -1 and self.remaining_tickets < num_tickets:
			return False
		return True

	@property
	def tickets_sold(self) -> int:
		"""Returns the number of tickets sold for this ticket type."""
		return frappe.db.count(
			"Event Ticket", {"ticket_type": self.name, "docstatus": 1}
		)

	@property
	def remaining_tickets(self) -> int:
		"""Returns -1 if no limit, otherwise the number of remaining tickets."""
		if not self.max_tickets_available:
			return -1
		return self.max_tickets_available - self.tickets_sold

	def validate(self):
		self.create_linked_item()

	def create_linked_item(self):
		if not self.linked_item:
			if frappe.db.exists("Item", "Ticket"):
				self.linked_item = "Ticket"
			else:
				item = frappe.get_doc(
					{
						"doctype": "Item",
						"item_code": "Ticket",
						"item_group": "Services",
						"stock_uom": "Nos",
						"is_stock_item": 0,
					}
				)
				item.insert()
				self.linked_item = item.name
