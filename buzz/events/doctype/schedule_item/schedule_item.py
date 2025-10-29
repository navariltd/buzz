# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ScheduleItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		date: DF.Date
		description: DF.Data | None
		end_time: DF.Time
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		start_time: DF.Time
		talk: DF.Link | None
		track: DF.Link
		type: DF.Literal["Talk", "Break"]
	# end: auto-generated types

	pass
