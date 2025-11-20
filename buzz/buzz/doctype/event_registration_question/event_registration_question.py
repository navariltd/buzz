# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class EventRegistrationQuestion(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		help_text: DF.SmallText | None
		is_required: DF.Check
		options: DF.SmallText | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		question: DF.SmallText
		question_id: DF.Data
		question_type: DF.Literal["Text", "Select", "MultiSelect", "Rating", "Date", "Yes/No", "Email", "Phone"]
	# end: auto-generated types
	pass
