import frappe
from frappe.utils import nowdate, getdate
from frappe import _
from erpnext.accounts.doctype.payment_entry.payment_entry import (
    get_payment_entry,
)


@frappe.whitelist()
def initialize_payment(event_booking):
    try:
        event_booking = frappe.get_doc("Event Booking", event_booking)

        user = frappe.get_doc("User", frappe.session.user)

        user_details = frappe._dict(
            {
                "fullname": user.full_name,
                "email": user.email,
                "mobile": user.phone,
            }
        )

        customer = frappe.db.exists("Customer", {"email_id": user.email})

        if customer:
            customer = frappe.get_doc("Customer", customer)
        else:
            customer = create_customer(user_details)
            customer = frappe.get_doc("Customer", customer)

        payment_request = make_payment_request(customer, event_booking)

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Payment Initialization Failed"))
        frappe.throw(
            frappe._(
                "There was an error in processing your payment. Please contact support."
            )
        )

    return payment_request


def create_customer(user_details):
    customer = frappe.new_doc("Customer")
    customer.customer_name = user_details.fullname
    customer.customer_type = "Individual"
    customer.customer_group = frappe.db.get_single_value(
        "Selling Settings", "customer_group"
    )
    customer.territory = frappe.db.get_single_value("Selling Settings", "territory")
    customer.flags.ignore_mandatory = True
    customer.insert(ignore_permissions=True)

    try:
        frappe.db.savepoint("contact_creation")
        contact = frappe.new_doc("Contact")
        contact.first_name = user_details.fullname
        if user_details.mobile:
            contact.add_phone(
                user_details.mobile, is_primary_phone=1, is_primary_mobile_no=1
            )
        if user_details.email:
            contact.add_email(user_details.email, is_primary=1)
        contact.insert(ignore_permissions=True)

        contact.append(
            "links", {"link_doctype": "Customer", "link_name": customer.name}
        )

        contact.save(ignore_permissions=True)

    except frappe.DuplicateEntryError:
        return customer.name

    except Exception as e:
        frappe.db.rollback(save_point="contact_creation")
        frappe.log_error(frappe.get_traceback(), _("Contact Creation Failed"))
        pass

    return customer.name


def make_payment_request(customer, event_booking):
    try:
        payment_request = frappe.get_doc(
            {
                "doctype": "Payment Request",
                "payment_request_type": "Inward",
                "transaction_date": nowdate(),
                "party_type": "Customer",
                "status": "Initiated",
                "party": customer.name,
                "reference_doctype": "Event Booking",
                "reference_name": event_booking.name,
                "currency": event_booking.currency,
                "grand_total": event_booking.amount,
                "email_to": customer.email_id,
                "subject": _("Payment Request for {0} Event Booking").format(
                    event_booking.name
                ),
                "message": _("Please pay {0} {1} to renew your event booking.").format(
                    event_booking.currency, event_booking.amount
                ),
            }
        )

        payment_request.flags.ignore_validate = True
        payment_request.insert(ignore_permissions=True)
        payment_request.submit()

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            f"Payment Request Creation Failed for customer {customer.name}",
        )
        frappe.throw(
            frappe._(
                "There was an error in processing your payment. Please contact support."
            )
        )

    return payment_request


@frappe.whitelist()
def generate_invoice(event_booking, customer):

    try:

        invoice = make_invoice(event_booking, customer)

        make_payment_entry(event_booking, invoice)

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            f"Invoice Creation Failed for customer {customer.name}",
        )
        frappe.throw(
            frappe._(
                "There was an error in processing your invoice. Please contact support."
            )
        )


def make_invoice(event_booking, customer):
    try:

        invoice_items = []

        for attendee in event_booking.attendees:
            ticket_type = attendee.ticket_type
            linked_item = frappe.db.get_value(
                "Event Ticket Type", ticket_type, "linked_item"
            )
            if linked_item:
                event_booking.item_code = linked_item
                event_booking.qty = 1
                event_booking.rate = frappe.db.get_value(
                    "Event Ticket Type", ticket_type, "price"
                )

                invoice_items.append(
                    {
                        "item_code": linked_item,
                        "qty": 1,
                        "rate": event_booking.rate,
                    }
                )
            else:
                frappe.throw(
                    frappe._(f"Please set Linked Item for Ticket Type {ticket_type}")
                )

        invoice = frappe.new_doc("Sales Invoice")
        invoice.customer = customer.name
        invoice.currency = event_booking.currency
        invoice.company = event_booking.company
        invoice.items = invoice_items
        invoice.insert(ignore_permissions=True)
        invoice.submit()
    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            f"Invoice Creation Failed for customer {customer.name}",
        )
        frappe.throw(
            frappe._(
                "There was an error in processing your invoice. Please contact support."
            )
        )

    return invoice


def make_payment_entry(invoice):
    try:
        from erpnext.accounts.doctype.payment_entry.payment_entry import (
            get_payment_entry,
        )

        frappe.flags.ignore_account_permission = True
        pe = get_payment_entry(dt="Sales Invoice", dn=invoice.name)
        frappe.flags.ignore_account_permission = False

        pe.paid_to = frappe.db.get_value(
            "Company", invoice.company, "default_bank_account"
        )
        pe.reference_no = invoice.name
        pe.reference_date = getdate()
        pe.flags.ignore_mandatory = True
        pe.save()
        pe.submit()

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            f"Payment Entry Creation Failed for {invoice.customer}",
        )
        frappe.throw(
            _("There was an error creating your payment entry. Please contact support.")
        )

    return pe
