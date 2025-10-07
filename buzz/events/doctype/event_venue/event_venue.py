# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EventVenue(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		address: DF.SmallText
		latitude: DF.Float
		longitude: DF.Float
	# end: auto-generated types

	def validate(self):
		self.set_geojson_for_location()

	def set_geojson_for_location(self):
		if self.latitude and self.longitude:
			self.location = {
				"type": "FeatureCollection",
				"features": [
					{
						"type": "Feature",
						"properties": {},
						"geometry": {
							"type": "Point",
							"coordinates": [self.longitude, self.latitude],
						},
					}
				],
			}
			self.location = frappe.as_json(self.location)
