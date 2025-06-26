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


def get_list_orders(status: str = "0", orderidlist: str = "", numberlist: str = "") -> dict:
	"""
	Fetch a list of orders based on their status and optional filters.
	:param status: str - Status of the orders to fetch.
		Status codes:
		0 - Pending
		1 - Success
		2 - Voided
		3 - Waiting
		4 - Returned
		5 - Packed
		6 - Shipping
		7 - Failed Shipment
		Example: "0,1,3,4"
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

def update_product_available_stock_list(warehouse: str, data: dict) -> dict:
	"""
	Update the available stock for a product in a specific warehouse.
	:param warehouse: str - The warehouse where the stock is to be updated.
	:param data: dict - JSON data containing product details and stock information.
	:return: dict - JSON response from the Zort API after updating stock.

	note: Data structure should be like:
	{
		"stocks": [
			{
				"sku": "P0012",
				"stock": 399,
				"cost": 100
			},
			{
				"sku": "P378",
				"stock": 12,
				"cost": 200
			}
		]
	}
	On Zort SKU refer to Item Code in ERPNext.
	"""
	HEADER.update({"warehouse": warehouse})

	try:
		response = requests.post(
			f"{URL}/v4/Product/UpdateProductAvailableStockList",
			headers=HEADER,
			data=json.dumps(data),
			timeout=20
		)
		response.raise_for_status()
		res = response.json()
		return res
	except requests.RequestException as e:
		frappe.log_error(frappe.get_traceback(), _("Error updating product stock in Zort"))
		print(_("Failed to update product stock in Zort: {0}").format(str(e)))

def get_products(sku: str = "") -> dict:
	"""
	Fetch a list of products from Zort.
	:param sku: str - SKU of the product to fetch (optional).
	:return: dict - JSON response containing the list of products.

	Note: If SKU is provided, it will return details for that specific product.
	"""
	HEADER.update({"sku": sku})

	PARAMS = {
		# "limit": 50,
		# "page": 1,
		# "variationid": 107866,
		# "warehousecode": "W0001",
		# "inventorystatus": 0,
		# "createdafter": "2021-09-15",
		# "createdbefore": "2021-09-15",
		# "updatedafter": "2021-09-15",
		# "updatedbefore": "2021-09-15",
		# "categoryid": 123,
		"searchsku": sku,
	}
	try:
		response = requests.get(
			f"{URL}/v4/Product/GetProducts",
			headers=HEADER,
			params=PARAMS,
			timeout=20
		)
		response.raise_for_status()
		data = response.json()
		return data
	except requests.RequestException as e:
		frappe.log_error(frappe.get_traceback(), _("Error fetching products from Zort"))
		print(_("Failed to fetch products from Zort: {0}").format(str(e)))


def add_product(data: dict) -> dict:
	"""
	Add a new product to Zort.
	:param data: dict - JSON data containing product details.
	:return: dict - JSON response from the Zort API after adding the product.

	Note: Data structure should be like:
	{
		"sku": "P0014",
		"name": "Wit Day - Vitamin B",
		"sellprice": "20.00",
		"purchaseprice": "10.00",
		"unittext": "Piece",
		"weight": "500",
		"sell_vat_status": 2,
		"purchase_vat_status": 2
	}
	"""

	try:
		response = requests.post(
			f"{URL}/v4/Product/AddProduct",
			headers=HEADER,
			data=json.dumps(data),
			timeout=20
		)
		response.raise_for_status()
		res = response.json()
		return res
	except requests.RequestException as e:
		frappe.log_error(frappe.get_traceback(), _("Error adding product to Zort"))
		print(_("Failed to add product to Zort: {0}").format(str(e)))

def update_product(id: int, data: dict) -> dict:
	"""
	Update an existing product in Zort.
	:param id: int - ID of the product to update.
	:param data: dict - JSON data containing product details.
	:return: dict - JSON response from the Zort API after updating the product.

	Note: Data structure should be like:
	{
		"sku": "P0014",
		"name": "Wit Day - Vitamin B",
		"sellprice": "20.00",
		"purchaseprice": "10.00",
		"unittext": "Piece",
		"weight": "500",
		"sell_vat_status": 2,
		"purchase_vat_status": 2
	}
	"""
	PARAMS = {
		"id": id,
	}

	try:
		response = requests.post(
			f"{URL}/v4/Product/UpdateProduct",
			headers=HEADER,
			params=PARAMS,
			data=json.dumps(data),
			timeout=20
		)
		response.raise_for_status()
		res = response.json()
		return res
	except requests.RequestException as e:
		frappe.log_error(frappe.get_traceback(), _("Error updating product in Zort"))
		print(_("Failed to update product in Zort: {0}").format(str(e)))


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
