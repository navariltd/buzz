// Copyright (c) 2025, BWH Studios and contributors
// For license information, please see license.txt

frappe.ui.form.on("Event Booking", {
	refresh(frm) {
		frm.set_query("ticket_type", "attendees", (doc, cdt, cdn) => {
			return {
				filters: {
					event: doc.event,
				},
			};
		});

		// set_mop(frm);

		if (!frm.is_new()) {
			frm.add_custom_button("Request Payment", () => {
				frappe.prompt(
					[
						{
							fieldname: "phone_number",
							label: __("Phone Number"),
							fieldtype: "Data",
							reqd: 1,
							description: __("Enter the phone number for payment request"),
						},
					],
					(values) => {
						frm.call({
							doc: frm.doc,
							method: "initialize_payment",
							args: { phone_number: values.phone_number },
							freeze: true,
							freeze_message: __("Requesting Payment"),
							callback: function (r) {
								if (r.invoice) frm.reload_doc();
							},
						});
					},
					__("Enter Phone Number"),
					__("Request Payment")
				);
			});
		}

		!frm.doc.invoice &&
			frm.add_custom_button("Generate Invoice", () => {
				frm.call({
					doc: frm.doc,
					method: "generate_invoice",
					args: { save: true },
					freeze: true,
					freeze_message: __("Creating Membership Invoice"),
					callback: function (r) {
						if (r.invoice) frm.reload_doc();
					},
				});
			});
	},

	event(frm) {
		// set_mop(frm);
	},
});

function set_mop(frm) {
	if (!frm.doc.event || frm.doc.mode_of_payment) return;
	frappe.db.get_value("FE Event", frm.doc.event, "mode_of_payment").then((r) => {
		if (r.message && r.message.mode_of_payment) {
			frm.set_value("mode_of_payment", r.message.mode_of_payment);
		}
	});
}
