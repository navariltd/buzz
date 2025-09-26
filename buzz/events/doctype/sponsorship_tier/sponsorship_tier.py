# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

from buzz.payments import mark_payment_as_received


class SponsorshipTier(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		currency: DF.Link | None
		event: DF.Link
		price: DF.Currency
		title: DF.Data
	# end: auto-generated types

	pass
