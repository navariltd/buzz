# Copyright (c) 2025, BWH Studios and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]


class IntegrationTestBulkTicketCoupon(IntegrationTestCase):
	"""
	Integration tests for BulkTicketCoupon.
	Use this class for testing interactions between multiple components.
	"""

	def test_number_of_claimed_tickets_and_overage_prevention(self):
		test_event = frappe.get_doc("FE Event", {"route": "test-route"})
		test_sponsor_ticket_type = frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": test_event.name,
				"title": "Sponsor Pass",
				"is_published": True,
			}
		).insert()

		test_coupon = frappe.get_doc(
			{
				"doctype": "Bulk Ticket Coupon",
				"event": test_event.name,
				"ticket_type": test_sponsor_ticket_type.name,
				"number_of_granted_tickets": 2,
			}
		).insert()
		self.assertEqual(test_coupon.number_of_claimed_tickets, 0)

		frappe.get_doc(
			{
				"doctype": "Event Ticket",
				"attendee_name": "John Doe",
				"ticket_type": test_coupon.ticket_type,
				"coupon_used": test_coupon.code,
				"attendee_email": "john@email.com",
			}
		).insert().submit()
		self.assertEqual(test_coupon.number_of_claimed_tickets, 1)

		frappe.get_doc(
			{
				"doctype": "Event Ticket",
				"attendee_name": "John Doe",
				"ticket_type": test_coupon.ticket_type,
				"coupon_used": test_coupon.code,
				"attendee_email": "john@email.com",
			}
		).insert().submit()
		self.assertEqual(test_coupon.number_of_claimed_tickets, 2)

		# Max were 2
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Event Ticket",
					"attendee_name": "Jacob Doe",
					"ticket_type": test_coupon.ticket_type,
					"coupon_used": test_coupon.code,
					"attendee_email": "jenny@email.com",
				}
			).insert().submit()
