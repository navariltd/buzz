# Copyright (c) 2025, BWH Studios and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]

TEST_ADD_ON_PRICE = 100
TEST_VIP_TICKET_TYPE_PRICE = 500


class IntegrationTestEventBooking(IntegrationTestCase):
	"""
	Integration tests for EventBooking.
	Use this class for testing interactions between multiple components.
	"""

	def test_total_calculation_without_taxes(self):
		test_event = frappe.get_doc("Buzz Event", {"route": "test-route"})

		# Turn off GST for this test
		event_settings = frappe.get_doc("Buzz Settings")
		event_settings.apply_gst_on_bookings = False
		event_settings.save()

		test_ticket_add_on = frappe.get_doc(
			{
				"doctype": "Ticket Add-on",
				"event": test_event.name,
				"title": "T-Shirt",
				"price": TEST_ADD_ON_PRICE,
			}
		).insert()

		test_ticket_type = frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": test_event.name,
				"title": "VIP",
				"price": TEST_VIP_TICKET_TYPE_PRICE,
			}
		).insert()

		test_booking = frappe.get_doc(
			{
				"doctype": "Event Booking",
				"event": test_event.name,
				"user": "Administrator",
				"attendees": [
					{"ticket_type": test_ticket_type.name, "full_name": "John", "email": "john@email.com"},
					{"ticket_type": test_ticket_type.name, "full_name": "Jenny", "email": "jenny@email.com"},
				],
			}
		).insert()

		# without add ons
		self.assertEqual(test_booking.total_amount, 1000)

		test_attendee_add_on = frappe.get_doc(
			{
				"doctype": "Attendee Ticket Add-on",
				"add_ons": [{"add_on": test_ticket_add_on.name, "value": "XL"}],
			}
		).insert()

		test_booking.attendees[0].add_ons = test_attendee_add_on.name
		test_booking.save()

		# with one add-on
		self.assertEqual(test_booking.attendees[0].number_of_add_ons, 1)
		self.assertEqual(test_booking.attendees[0].add_on_total, TEST_ADD_ON_PRICE)
		self.assertEqual(test_booking.net_amount, 1100)
		self.assertEqual(test_booking.total_amount, 1100)

	def test_total_calculation_with_taxes(self):
		test_event = frappe.get_doc("Buzz Event", {"route": "test-route"})

		# Turn on GST for this test
		event_settings = frappe.get_doc("Buzz Settings")
		event_settings.apply_gst_on_bookings = True
		event_settings.gst_percentage = 18
		event_settings.save()

		test_ticket_type = frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": test_event.name,
				"title": "VIP",
				"price": TEST_VIP_TICKET_TYPE_PRICE,
			}
		).insert()

		test_booking = frappe.get_doc(
			{
				"doctype": "Event Booking",
				"event": test_event.name,
				"user": "Administrator",
				"attendees": [
					{"ticket_type": test_ticket_type.name, "full_name": "John", "email": "john@email.com"},
					{"ticket_type": test_ticket_type.name, "full_name": "Jenny", "email": "jenny@email.com"},
				],
			}
		).insert()

		self.assertEqual(test_booking.net_amount, 1000)
		self.assertEqual(test_booking.tax_percentage, 18)
		self.assertEqual(test_booking.tax_amount, 180)
		self.assertEqual(test_booking.total_amount, 1180)

	def test_prevents_booking_if_tickets_unavailable(self):
		test_event = frappe.get_doc("Buzz Event", {"route": "test-route"})
		test_vip_ticket_type = frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": test_event.name,
				"title": "VIP",
				"price": 500,
				"is_published": True,
				"max_tickets_available": 2,
			}
		).insert()

		test_normal_ticket_type = frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": test_event.name,
				"title": "Normal",
				"price": 500,
				"is_published": True,
			}
		).insert()

		# VIP Ticket 1
		frappe.get_doc(
			{
				"doctype": "Event Ticket",
				"ticket_type": test_vip_ticket_type.name,
				"attendee_name": "John Doe",
				"attendee_email": "john@email.com",
			}
		).insert().submit()

		# VIP Ticket 2 with Normal Ticket 1
		frappe.get_doc(
			{
				"doctype": "Event Booking",
				"user": frappe.session.user,
				"event": test_event.name,
				"attendees": [
					{
						"full_name": "John Doe",
						"ticket_type": test_vip_ticket_type.name,
						"email": "john@email.com",
					},
					{
						"full_name": "Jenny Doe",
						"ticket_type": test_normal_ticket_type.name,
						"email": "jenny@email.com",
					},
				],
			}
		).insert().submit()

		# VIP Ticket 3 with Normal Ticket 2
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Event Booking",
					"user": frappe.session.user,
					"event": test_event.name,
					"attendees": [
						{
							"full_name": "John Doe",
							"ticket_type": test_vip_ticket_type.name,
							"email": "john@email.com",
						},
						{
							"full_name": "John Doe",
							"ticket_type": test_normal_ticket_type.name,
							"email": "john@email.com",
						},
					],
				}
			).insert()

		# Unpublish normal ticket type
		test_normal_ticket_type.is_published = False
		test_normal_ticket_type.save()

		# Booking with unpublished ticket type
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Event Booking",
					"user": frappe.session.user,
					"event": test_event.name,
					"attendees": [
						{
							"full_name": "John Doe",
							"ticket_type": test_normal_ticket_type.name,
							"email": "john@email.com",
						}
					],
				}
			).insert()
