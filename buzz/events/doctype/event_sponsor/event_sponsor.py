# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class EventSponsor(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		company_logo: DF.AttachImage
		company_name: DF.Data
		enquiry: DF.Link | None
		event: DF.Link
		tier: DF.Link
	# end: auto-generated types

	pass
