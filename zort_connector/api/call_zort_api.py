import requests
import json

import frappe
from frappe import _

ZORT_SETTING = frappe.get_doc("Zort Setting")

URL = ZORT_SETTING.zort_endpoint_url
STORENAME = ZORT_SETTING.storename
APIKEY = ZORT_SETTING.apikey
APISECRET = ZORT_SETTING.apisecret

HEADER = {
	"storename": STORENAME,
	"apikey": APIKEY,
	"apisecret": APISECRET,
}


def get_list_orders(status: int = 0, orderidlist: str = "", numberlist: str = "") -> dict:
	"""
	Fetch a list of orders based on their status and optional filters.
	:param status: int - Status of the orders to fetch.
		Status codes:
		0 - Pending
		1 - Success
		2 - Voided
		3 - Waiting
		4 - Returned
		5 - Packed
		6 - Shipping
		7 - Failed Shipment
		Example: 0 (for Pending orders)
	:param orderidlist: str - Comma-separated list of order IDs to filter (optional).
	:param numberlist: str - Comma-separated list of order numbers to filter (optional).
	:return: dict - JSON response containing the list of orders.
	"""
	HEADER.update({
		"orderidlist": orderidlist,
		"numberlist": numberlist
	})

	PARAMS = {
		# "page": 1,
		# "keyword": "IV-2020",
		# "createdafter": "2020-12-24",
		# "createdbefore": "2020-12-27",
		# "updatedafter": "2021-06-10",
		# "updatedbefore": "2021-01-30",
		# "orderdateafter": "2020-12-15",
		# "orderdatebefore": "2020-12-15",
		# "paymentafter": "2020-12-15",
		# "paymentbefore": "2020-12-15",
		"status": status,
		# "fromamount": 0,
		# "toamount": 10000,
		# "frompaymentamount": 0,
		# "topaymentamount": 10000,
		# "limit": 2
	}

	try:
		response = requests.get(
			f"{URL}/v4/Order/GetOrders",
			headers=HEADER,
			params=PARAMS,
			timeout=20
		)
		response.raise_for_status()
		data = response.json()
		return data
	except requests.RequestException as e:
		frappe.log_error(frappe.get_traceback(), _("Error fetching orders from Zort"))
		print(_("Failed to fetch orders from Zort: {0}").format(str(e)))


# def create_api_logs():
# 	"""
# 	Create an API log entry for the Zort Connector API.
# 	This function logs the API request details for tracking and debugging purposes.
# 	"""
# 	# Create an API Log doctype
# 	api_log_data = {
# 		"doctype": "API Request Log",
# 		"path": "/api/method/zort_connector.api.custom_api.create_sales_order_from_zort",
# 		"method": "POST",
# 		"user": frappe.session.user,
# 	}

# 	try:
# 		api_log = frappe.get_doc(api_log_data)
# 		api_log.insert()
# 		frappe.db.commit()
# 		print(f"API Log created successfully: {api_log.name}")
# 	except Exception as e:
# 		frappe.log_error(frappe.get_traceback(), _("Error creating API Log"))
# 		print(f"Error creating API Log: {str(e)}")
