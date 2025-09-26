// Copyright (c) 2025, BWH Studios and contributors
// For license information, please see license.txt

frappe.ui.form.on("FE Event", {
	refresh(frm) {
		frappe.call("frappe.geo.country_info.get_country_timezone_info").then(({ message }) => {
			frm.fields_dict.time_zone.set_data(message.all_timezones);
		});

		if (frm.doc.route && frm.doc.is_published) {
			frm.add_web_link(`/events/${frm.doc.route}`);
		}

		frm.add_custom_button(__("Start Check In"), () => {
			frappe.prompt(
				{
					label: "Track",
					fieldname: "track",
					fieldtype: "Link",
					options: "Event Track",
					get_query() {
						return {
							filters: {
								event: frm.doc.name,
							},
						};
					},
				},
				(values) => {
					const track = values.track;
					new frappe.ui.Scanner({
						dialog: true, // open camera scanner in a dialog
						multiple: false, // TODO: make multiple work (Danny says use a prev variable to avoid duplicate)
						on_scan(data) {
							const ticket_id = data.decodedText;
							frm.call("check_in", { ticket_id, track })
								.then(() => {
									frappe.show_alert(__("Check In Complete!"));
									frm.refresh();
								})
								.catch(() => {
									frappe.utils.play_sound("error");
								});
						},
					});
				}
			);
		});

		const button_label = frm.doc.is_published ? __("Unpublish") : __("Publish");
		frm.add_custom_button(button_label, () => {
			frm.set_value("is_published", !frm.doc.is_published);
			frm.save();
		});

		frm.set_query("track", "schedule", (doc, cdt, cdn) => {
			return {
				filters: {
					event: doc.name,
				},
			};
		});
	},
});
