# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AdditionalEventPage(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		content: DF.TextEditor | None
		event: DF.Link
		is_published: DF.Check
		route: DF.Data | None
		title: DF.Data
	# end: auto-generated types

	def validate(self):
		self.validate_route()

	def validate_route(self):
		if self.is_published and not self.route:
			event_is_published, event_route = frappe.db.get_value(
				"FE Event", self.event, ["is_published", "route"]
			)

			if not event_is_published:
				frappe.throw(frappe._("Event must be published before publishing additional pages."))

			self.route = frappe.website.utils.cleanup_page_name(self.title).replace("_", "-")
			self.route = event_route + "/" + self.route
