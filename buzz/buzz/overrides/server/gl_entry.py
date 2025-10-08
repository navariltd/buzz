import frappe
from frappe import _
from frappe.model.document import Document
from ....payment import check_and_validate_payment


@frappe.whitelist()
def on_update(doc: Document, method: str) -> None:
    if doc.against_voucher_type == "Sales Invoice" and doc.against_voucher:
        check_and_validate_payment(doc.against_voucher)
