# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class EventAttendeeRegistration(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		email: DF.Data
		full_name: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		personnel_type: DF.Data
		phone_number: DF.Data
	# end: auto-generated types
	pass
