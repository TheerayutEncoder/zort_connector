import frappe
from frappe import _, _dict
from zort_connector.api import call_zort_api


def create_sales_order_from_zort():
	"""
	Create a Sales Order from Zort data.
	This function is called by the Zort Connector to create a Sales Order in Frappe.
	"""

	sales_order_list = call_zort_api.get_list_orders()
	if not sales_order_list:
		return {"status": "error", "message": _("Failed to fetch orders from Zort.")}
	order_list = sales_order_list.get("list", [])
	if not order_list:
		return {"status": "error", "message": _("No orders found in Zort.")}
	print(order_list)
	print("length of order_list:", len(order_list))
	print(type(order_list[0]))
	# for order in order_list:
	# 	prepared_data = prepare_data(order)



	return {"status": "success", "message": _("Sales Order created successfully.")}

def prepare_data(data: dict):
	"""
	Prepare data for creating a Sales Order.
	This function can be customized to transform the incoming data as needed.
	"""
	if not isinstance(data, dict):
		logger.error("Invalid data format: Expected a dictionary.")
		return {"status": "error", "message": _("Invalid data format.")}
	prepared_data = {
		"customer": data.get("customername"),
		"date": frappe.utils.nowdate(),
		"delivery_date": frappe.utils.nowdate(),
		"items": [
			{
				"item_code": item.get("item_code"),
				"qty": item.get("qty"),
				"unit": item.get("unit"),
			}
			for item in data.get("list", [])
		],
	}

	return prepared_data

def update_sales_order_from_zort(data):
	"""
	Update an existing Sales Order with data from Zort.
	This function can be customized to update the Sales Order as needed.
	"""
	if not isinstance(data, dict):
		logger.error("Invalid data format: Expected a dictionary.")
		return {"status": "error", "message": _("Invalid data format.")}

	# Example update logic (customize as needed)
	# sale_order = frappe.get_doc("Sales Order", data.get("name"))
	# sale_order.update(data)
	# sale_order.save()

	return {"status": "success", "message": _("Sales Order updated successfully.")}

def cancel_sales_order_from_zort(data):
	"""
	Cancel a Sales Order based on data from Zort.
	This function can be customized to cancel the Sales Order as needed.
	"""
	if not isinstance(data, dict):
		logger.error("Invalid data format: Expected a dictionary.")
		return {"status": "error", "message": _("Invalid data format.")}

	# Example cancellation logic (customize as needed)
	# sale_order = frappe.get_doc("Sales Order", data.get("name"))
	# sale_order.cancel()

	return {"status": "success", "message": _("Sales Order cancelled successfully.")}



