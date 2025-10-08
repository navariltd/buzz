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
        invoice = frappe.db.get_value(
            "Sales Invoice",
            {"event_booking": event_booking.name, "docstatus": ["!=", 2]},
            "name",
        )
        payment_gateway = get_payment_gateway_from_mop(
            event_booking.mode_of_payment, event_booking.company
        )
        payment_gateway_account = frappe.db.get_value(
            "Payment Gateway Account",
            {"payment_gateway": payment_gateway, "company": event_booking.company},
            "name",
        )
        payment_request = frappe.get_doc(
            {
                "doctype": "Payment Request",
                "payment_request_type": "Inward",
                "transaction_date": nowdate(),
                "party_type": "Customer",
                "status": "Initiated",
                "party": customer.name,
                "reference_doctype": "Sales Invoice",
                "reference_name": invoice,
                "mode_of_payment": event_booking.mode_of_payment,
                "payment_gateway": payment_gateway,
                "payment_gateway_account": payment_gateway_account,
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
                        "event_booking": event_booking.name,
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
                "event_booking": event_booking.name,
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


def check_and_validate_payment(sales_invoice):
    try:
        invoice = frappe.get_doc("Sales Invoice", sales_invoice)

        event_booking = frappe.get_doc("Event Booking", invoice.event_booking)
        invoices = frappe.get_all(
            "Sales Invoice",
            filters={"event_booking": invoice.event_booking, "docstatus": ["!=", 2]},
            fields=["name", "grand_total", "outstanding_amount", "posting_date"],
            order_by="posting_date asc",
        )

        total_paid = 0
        for inv in invoices:
            if inv.outstanding_amount == 0:
                total_paid += inv.grand_total

        if (
            total_paid >= float(event_booking.total_amount)
            and event_booking.docstatus == 0
        ):
            event_booking.submit()
    except Exception as e:
        frappe.log_error(
            f"Payment validation failed for Sales Invoice {sales_invoice}",
            frappe.get_traceback(),
        )


@frappe.whitelist()
def get_payment_gateway_from_mop(mode_of_payment: str, company: str) -> str:
    payment_gateway = None
    try:
        if not frappe.db.exists("Mode of Payment", mode_of_payment):
            return None
        mop_doc = frappe.get_doc("Mode of Payment", mode_of_payment)
        account_entry = next(
            (acc for acc in mop_doc.accounts if acc.company == company), None
        )
        if account_entry:
            payment_account = account_entry.default_account
            if frappe.db.exists(
                "Payment Gateway Account", {"payment_account": payment_account}
            ):
                try:
                    pg_account = frappe.get_doc(
                        "Payment Gateway Account", {"payment_account": payment_account}
                    )
                    if pg_account and pg_account.payment_gateway:
                        payment_gateway = pg_account.payment_gateway
                except Exception:
                    pass
            else:
                default_pg_account = frappe.get_value(
                    "Payment Gateway Account", {"is_default": 1}, "payment_gateway"
                )
                if default_pg_account:
                    payment_gateway = default_pg_account
    except Exception:
        pass

    return payment_gateway
