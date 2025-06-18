from frappe.custom.doctype.custom_field.custom_field import \
    create_custom_fields

from zort_connector.constants import ZORT_CUSTOM_FIELDS


def after_app_install(app_name):
	print("Setting up ERPNext Thailand...")
	try:
		make_custom_fields()
		print("Installation complete.")
	except Exception as e:
		print(f"An error occurred: {e}")
		BUG_REPORT_URL = "https://github.com/ecosoft-frappe/erpnext_thailand/issues/new"
		click.secho(
			"Installation for ERPNext Thailand app failed due to an error."
			" Please try re-installing the app or"
			f" report the issue on {BUG_REPORT_URL} if not resolved.",
			fg="bright_red",
		)
		raise e

def make_custom_fields():
	print("Setup custom fields for erpnext...")
	create_custom_fields(ZORT_CUSTOM_FIELDS, ignore_validate=True)
