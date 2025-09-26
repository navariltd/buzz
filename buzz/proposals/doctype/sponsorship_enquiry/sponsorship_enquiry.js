// Copyright (c) 2025, BWH Studios and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sponsorship Enquiry", {
	refresh(frm) {
		if (frm.doc.status === "Approval Pending") {
			frm.add_custom_button(__("Approve"), () => {
				frm.set_value("status", "Payment Pending");
				frm.save();
			});
		}
	},
});
