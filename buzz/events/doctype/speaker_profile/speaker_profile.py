# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SpeakerProfile(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from buzz.events.doctype.social_media_link.social_media_link import SocialMediaLink

		company: DF.Data | None
		designation: DF.Data | None
		display_image: DF.AttachImage | None
		display_name: DF.Data | None
		name: DF.Int | None
		social_media_links: DF.Table[SocialMediaLink]
		user: DF.Link
	# end: auto-generated types

	pass


def update_speaker_display_name(doc, event=None):
	if doc.has_value_changed("full_name"):
		frappe.db.set_value("Speaker Profile", {"user": doc.name}, "display_name", doc.full_name)
