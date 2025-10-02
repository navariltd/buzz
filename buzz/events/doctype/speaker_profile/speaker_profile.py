# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SpeakerProfile(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from buzz.events.doctype.social_media_link.social_media_link import SocialMediaLink
		from frappe.types import DF

		company: DF.Data | None
		designation: DF.Data | None
		display_image: DF.AttachImage | None
		display_name: DF.Data
		full_name: DF.Data
		name: DF.Int | None
		social_media_links: DF.Table[SocialMediaLink]
	# end: auto-generated types

	pass
