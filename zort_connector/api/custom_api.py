import frappe
from frappe import _, _dict, get_cached_value
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

	for order in order_list:
		prepared_data = prepare_data(order)

		if prepared_data.get("status") == "error":
			continue

		try:
			print("prepared_data.get('zort_order_id')", prepared_data.get('zort_order_id'))
			print("prepared_data.get('zort_sales_order_no')", prepared_data.get('zort_sales_order_no'))
			sales_order = frappe.get_doc({
				"doctype": "Sales Order",
				**prepared_data
			})
			sales_order.insert()
			frappe.db.commit()
			print(f"Sales Order created: {sales_order.name}")
			frappe.logger().info(f"Sales Order created: {sales_order.name}")
		except Exception as e:
			print(f"Failed to create Sales Order: {str(e)}")
			frappe.logger().error(f"Failed to create Sales Order: {str(e)}")


def prepare_data(data: dict):
	"""
	Prepare data for creating a Sales Order.
	This function can be customized to transform the incoming data as needed.
	"""
	if not isinstance(data, dict):
		logger.error("Invalid data format: Expected a dictionary.")
		return {"status": "error", "message": _("Invalid data format.")}

	customer = create_customer_from_zort(data)
	if not customer:
		return {"status": "error", "message": _("Failed to create or find customer.")}

	items = []
	for item in data.get("list", []):
		sku = item.get("sku")
		item_code = sku if frappe.db.exists("Item", sku) else create_item_from_zort(item)

		items.append({
			"item_code": item_code,
			"delivery_date": frappe.utils.today(),
			"qty": float(item.get("number", 0) or 0),
			"uom": item.get("unittext"),
			"price_list_rate": float(item.get("pricepernumber", 0) or 0),
			"discount_amount": float(item.get("discountPerNumber", 0) or 0),
			"amount": float(item.get("totalprice", 0) or 0),
		})

	prepared_data = {
		"customer": customer,
		"transaction_date": data.get("orderdateString"),
		"order_type": "Sales",
		"zort_order_id": data.get("id"),
		"zort_sales_order_no": data.get("number"),
		"zort_sales_channel": data.get("saleschannel"),
		"zort_order_status": data.get("status"),
		"tracking_no": data.get("trackingno"),
		"sales_channel": data.get("saleschannel"),
		"payment_status": data.get("paymentstatus"),
		"items": items,
	}

	frappe.logger().info("Prepared data for Sales Order: {}".format(prepared_data))

	return prepared_data


def create_item_from_zort(item: dict) -> str:
	"""
	Create an Item from Zort data.
	This function can be customized to create an Item in Frappe.
	"""
	item_code = item.get("sku")
	if not item_code:
		frappe.logger().error("Item code is required to create an item.")
		return {"status": "error", "message": _("Item code is required.")}

	default_stock_uom = get_cached_value("Stock Settings", None, "stock_uom")
	try:
		item_doc = frappe.get_doc({
			"doctype": "Item",
			"item_code": item_code,
			"item_name": item.get("name", item_code),
			"item_group": "Products",
			"stock_uom": item.get("unittext", default_stock_uom),
			"is_stock_item": 1,
		})
		item_doc.insert()
		frappe.db.commit()
		frappe.logger().info(f"Item created: {item_doc.name}")
	except Exception as e:
		frappe.logger().error(f"Failed to create Item: {str(e)}")

	return item_code


def create_customer_from_zort(data: dict) -> str:
	"""
	Create a Customer from Zort data.
	This function can be customized to create a Customer in Frappe.
	"""
	customer_name = data.get("customername")
	phone_number = data.get("customerphone")
	if not customer_name:
		frappe.log_error("Customer name is required to create a customer.")
		return ""

	address_name = frappe.db.get_value("Address", {"phone": phone_number}, "name")
	if address_name:
		address_doc = frappe.get_doc("Address", address_name)
		links = address_doc.links or []
		for link in links:
			if link.link_doctype == "Customer":
				return link.link_name
	else:
		try:
			customer_doc = frappe.get_doc({
				"doctype": "Customer",
				"customer_name": customer_name,
			})
			customer_doc.insert()
			print("customer_doc", customer_doc)
			print("customer_doc.name", customer_doc.name)

			address_doc = frappe.get_doc({
				"doctype": "Address",
				"address_title": customer_name,
				"address_type": "Billing",
				"address_line1": "{} {} {}".format(
					data.get("customerstreetAddress") or "",
					data.get("customersubdistrict") or "",
					data.get("customerdistrict") or ""
				).strip(),
				"city": data.get("customerprovince", ""),
				"state": data.get("customerstate", ""),
				"pincode": data.get("customerpostcode", ""),
				"phone": phone_number,
				"email_id": data.get("customeremail", ""),
				"tax_id": data.get("customeridnumber", ""),
				"links": [{
					"link_doctype": "Customer",
					"link_name": customer_doc.name
				}]
			})
			address_doc.insert()
			print("address_doc", address_doc)
			print("address_doc.name", address_doc.name)
			frappe.db.commit()
		except Exception as e:
			frappe.logger().error(f"Failed to create Customer or Address: {str(e)}")
			return ""
	return customer_name


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

# def cancel_sales_order_from_zort(data):
# 	"""
# 	Cancel a Sales Order based on data from Zort.
# 	This function cancels the Sales Order in Frappe based on the provided Zort data.
# 	"""
# 	if not isinstance(data, dict):
# 		frappe.logger().error("Invalid data format: Expected a dictionary.")
# 		return {"status": "error", "message": _("Invalid data format.")}

# 	sales_order_name = frappe.db.get_value("Sales Order", {"zort_order_id": data.get("id")}, "name")
# 	if not sales_order_name:
# 		frappe.logger().error(f"Sales Order not found for Zort Order ID: {data.get('id')}")
# 		return {"status": "error", "message": _("Sales Order not found.")}

# 	try:
# 		sales_order = frappe.get_doc("Sales Order", sales_order_name)
# 		sales_order.cancel()
# 		frappe.db.commit()
# 		frappe.logger().info(f"Sales Order cancelled: {sales_order_name}")
# 		return {"status": "success", "message": _("Sales Order cancelled successfully.")}
# 	except Exception as e:
# 		frappe.logger().error(f"Failed to cancel Sales Order: {str(e)}")
# 		return {"status": "error", "message": _("Failed to cancel Sales Order.")}



