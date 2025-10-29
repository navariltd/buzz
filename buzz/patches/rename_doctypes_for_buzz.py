import frappe

doctypes = {
	"Event Management Settings": "Buzz Settings",
	"FE Event": "Buzz Event",
}


def execute():
	rename_doctypes()
	create_sequences()


def rename_doctypes():
	for old in doctypes:
		new = doctypes[old]
		if not frappe.db.exists("DocType", new):
			print(f"Renaming {old} to {new}")
			frappe.rename_doc("DocType", old, new, force=True, ignore_if_exists=True)


def create_sequences():
	doctype = "Buzz Event"
	sequence_name = frappe.scrub(doctype + "_id_seq")
	frappe.db.sql_ddl(f"drop sequence if exists {sequence_name}")
	last_name = frappe.db.get_all(doctype, fields=["max(name) as last"])[0].last
	start_value = (last_name or 0) + 1
	print(f"Creating sequence for {doctype} starting at {start_value}")
	frappe.db.create_sequence(doctype, start_value=start_value, check_not_exists=True)
