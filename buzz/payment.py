import frappe
from frappe.utils import nowdate, getdate
from frappe import _
from erpnext.accounts.doctype.payment_entry.payment_entry import (
    get_payment_entry,
)


def create_customer(user_details):
    customer = frappe.new_doc("Customer")
    customer.customer_name = user_details.fullname
    customer.customer_type = "Individual"
    customer.email_id = user_details.email
    customer.mobile_no = user_details.mobile

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


def make_payment_request(customer, event_booking, phone_number=None):
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
                "payment_gateway": event_booking.payment_gateway,
                "currency": event_booking.currency,
                "grand_total": event_booking.total_amount,
                "email_to": customer.email_id,
                "subject": _("Payment Request for {0} Event Booking").format(
                    event_booking.name
                ),
                "message": _("Please pay {0} {1} to renew your event booking.").format(
                    event_booking.currency, event_booking.total_amount
                ),
            }
        )

        if phone_number:
            payment_request.phone_number = phone_number

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


def make_invoice(event_booking, customer):
    try:

        company = frappe.get_doc("Company", event_booking.company)

        # Get defaults from Company
        default_income_account = company.default_income_account
        default_expense_account = company.default_expense_account
        default_cost_center = company.cost_center

        invoice_items = []

        for attendee in event_booking.attendees:
            ticket_type = attendee.ticket_type
            linked_item = frappe.db.get_value(
                "Event Ticket Type", ticket_type, "linked_item"
            )
            if linked_item:
                # Get item doc to fetch its defaults
                item = frappe.get_doc("Item", linked_item)

                income_account = item.get("income_account") or default_income_account
                expense_account = item.get("expense_account") or default_expense_account
                cost_center = item.get("cost_center") or default_cost_center

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
                        "income_account": income_account,
                        "expense_account": expense_account,
                        "cost_center": cost_center,
                    }
                )
            else:
                frappe.throw(
                    frappe._(f"Please set Linked Item for Ticket Type {ticket_type}")
                )

        invoice = frappe.get_doc(
            {
                "doctype": "Sales Invoice",
                "customer": customer.name,
                "currency": event_booking.currency,
                "company": event_booking.company,
                "items": invoice_items,
            }
        )
        invoice.set_missing_values()

        invoice.insert(ignore_permissions=True)
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
