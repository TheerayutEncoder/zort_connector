import json
import frappe
from frappe import _, _dict, get_cached_value
from frappe.utils import strip_html_tags
from erpnext.stock.utils import get_stock_balance

from zort_connector.api import call_zort_api



def create_sales_order_from_zort():
	"""
	Create a Sales Order from Zort data.
	This function is called by the Zort Connector to create a Sales Order in Frappe.
	"""

	sales_order_list = call_zort_api.get_list_orders()
	if not sales_order_list:
		print("Failed to fetch orders from Zort.")
		return {"status": "error", "message": _("Failed to fetch orders from Zort.")}

	order_list = sales_order_list.get("list", [])
	if not order_list:
		print("No orders found in Zort.")
		return {"status": "error", "message": _("No orders found in Zort.")}

	# Get existing Zort Order IDs to avoid duplicates
	existing_zort_order_ids = get_existing_zort_order_ids()

	for order in order_list:
		prepared_data = prepare_data(order)

		if prepared_data.get("status") == "error":
			continue
		if prepared_data.get('zort_order_id') in existing_zort_order_ids:
			continue

		try:
			sales_order = frappe.get_doc({
				"doctype": "Sales Order",
				**prepared_data
			})
			sales_order.insert()
			frappe.db.commit()

			if check_if_sales_order_can_be_submitted(sales_order.name) and sales_order.docstatus == 0:
				# If the Sales Order can be submitted, submit it
				sales_order.submit()

			print(f"Sales Order created: {sales_order.name}")
		except Exception as e:
			print(f"Failed to create Sales Order: {str(e)}")
			frappe.logger().error(f"Failed to create Sales Order: {str(e)}")

def prepare_data(data: dict):
	"""
	Prepare data for creating a Sales Order.
	This function can be customized to transform the incoming data as needed.
	"""
	if not isinstance(data, dict):
		print("Invalid data format received from Zort.")
		return {"status": "error", "message": _("Invalid data format.")}

	customer = create_customer_from_zort(data)
	if not customer:
		print("Failed to create or find customer.")
		return {"status": "error", "message": _("Failed to create or find customer.")}

	warehouse = get_warehouse_from_zort(
		data.get("zort_sales_order_no"),
		data.get("trackingno"),
		data.get("description", "")
	)
	if not warehouse:
		print("Failed to get warehouse.")
		return {"status": "error", "message": _("Failed to get warehouse.")}

	items = []
	for item in data.get("list", []):

		uom = create_uom_from_zort(item)
		if not uom:
			print("Failed to create UOM.")
			return {"status": "error", "message": _("Failed to create UOM.")}

		sku = item.get("sku")
		item_code = sku if frappe.db.exists("Item", sku) else create_item_from_zort(item)

		items.append({
			"item_code": item_code,
			"delivery_date": frappe.utils.today(),
			"qty": float(item.get("number", 0) or 0),
			"uom": uom,
			"price_list_rate": float(item.get("pricepernumber", 0) or 0),
			"discount_amount": float(item.get("discountPerNumber", 0) or 0),
			"amount": float(item.get("totalprice", 0) or 0),
			"warehouse": warehouse,
		})

	# Add shipping fee as an item if it exists
	if data.get("shippingamount") > 0:
		if not frappe.db.exists("Item", "shipping-fee"):
			try:
				shipping_item = frappe.get_doc({
					"doctype": "Item",
					"item_code": "shipping-fee",
					"item_name": "Shipping fee",
					"item_group": "Services",
					"stock_uom": get_cached_value("Stock Settings", None, "stock_uom"),
					"is_stock_item": 0,
				})
				shipping_item.insert()
				frappe.db.commit()
				print(f"Shipping Item created: {shipping_item.name}")
			except Exception as e:
				print(f"Failed to create Shipping Item: {str(e)}")
				frappe.logger().error(f"Failed to create Shipping Item: {str(e)}")

		items.append({
			"item_code": "shipping-fee",
			"delivery_date": frappe.utils.today(),
			"qty": 1,
			"price_list_rate": float(data.get("shippingamount", 0) or 0),
			"discount_amount": 0.0,
			"warehouse": warehouse,
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
		"description": data.get("description", ""),
		"shipping_channel": data.get("shippingchannel"),
		"payment_status": data.get("paymentstatus"),
		"items": items,
		"discount_amount": float(data.get("discountamount", 0) or 0),
		"zort_api_order_data": json.dumps(data, indent=4, ensure_ascii=False),
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
			"sync_with_zort": 1,
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
	We check if the customer already exists based on the phone number. (Actually, it should be ID number))
	If the customer does not exist, we create a new Customer and Address.

	Note: If customer data following PDPA like J**n W*** (John Wick) return customer as 'Mr. Dummy Customer'
	"""
	customer_name = data.get("customername")
	phone_number = data.get("customerphone")
	if not customer_name:
		frappe.log_error("Customer name is required to create a customer.")
		return ""

	if "*" in customer_name or "*" in phone_number:
		if not frappe.db.exists("Customer", {"customer_name": "Mr. Dummy Customer"}):
			try:
				customer_doc = frappe.get_doc({
					"doctype": "Customer",
					"customer_name": "Mr. Dummy Customer",
				})
				customer_doc.insert()
				frappe.db.commit()
				print(f"Dummy Customer {customer_doc.name} has been created")
			except Exception as e:
				print(f"Failed to create Dummy Customer: {str(e)}")
				frappe.logger().error(f"Failed to create Dummy Customer: {str(e)}")
		return "Mr. Dummy Customer"

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
			print(f"Customer {customer_doc.name} has been created")

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
			print(f"Address {address_doc.name} has been created")
			frappe.db.commit()
		except Exception as e:
			print(f"Failed to create Customer or Address: {str(e)}")
			# Log the error for debugging purposes
			frappe.logger().error(f"Failed to create Customer or Address: {str(e)}")
			return ""
	return customer_name

def create_uom_from_zort(item: dict) -> str:
	"""
	Create a UOM (Unit of Measure) from Zort data.
	This function can be customized to create a UOM in Frappe.
	"""
	uom_name = item.get("unittext")

	if not uom_name:
		frappe.logger().error("UOM name is required to create a UOM.")
		return ""

	if not frappe.db.exists("UOM", {"uom_name": uom_name}):
		try:
			uom_doc = frappe.get_doc({
				"doctype": "UOM",
				"uom_name": uom_name,
				"uom_type": "Stock UOM"
			})
			uom_doc.insert()
			frappe.db.commit()
			print(f"UOM created: {uom_doc.name}")
			frappe.logger().info(f"UOM created: {uom_doc.name}")
		except Exception as e:
			print(f"Failed to create UOM: {str(e)}")
			frappe.logger().error(f"Failed to create UOM: {str(e)}")
	else:
		frappe.logger().info(f"UOM already exists: {uom_name}")

	return uom_name

def update_sales_order_from_zort():
	"""
	Update an existing Sales Order with data from Zort.
	This function can be customized to update the Sales Order as needed.
	"""
	existing_zort_order_ids = get_existing_zort_order_ids()
	existing_zort_order_ids_str = ",".join(map(str, existing_zort_order_ids))
	print("existing_zort_order_ids_str", existing_zort_order_ids_str)

	order_list = call_zort_api.get_list_orders(status="0,1,2",orderidlist=existing_zort_order_ids_str)

	if not order_list:
		print("Failed to fetch orders from Zort.")
		return {"status": "error", "message": _("Failed to fetch orders from Zort.")}

	for order in order_list.get("list", []):
		so_doc = frappe.get_doc("Sales Order", {"zort_order_id": order.get("id")})

		if so_doc:
			so_doc.zort_order_status = order.get("status")
			so_doc.payment_status = order.get("paymentstatus")
			so_doc.tracking_no = order.get("trackingno")
			so_doc.description = order.get("description", "")
			so_doc.zort_api_order_data = json.dumps(order, indent=4, ensure_ascii=False)
			# update warehouse in Items
			warehouse = get_warehouse_from_zort(
				zort_sales_order_no=so_doc.get("zort_sales_order_no"),
				tracking_no=so_doc.get("tracking_no"),
				description=so_doc.get("description", "")
			)
			print(f"Warehouse for Sales Order {so_doc.name}: {warehouse}")
			if so_doc.docstatus == 0:
				for item in so_doc.items:
					item.warehouse = warehouse
			so_doc.save()

			# Submit Sales Order if check_if_sales_order_can_be_submitted
			if so_doc.docstatus == 0 and check_if_sales_order_can_be_submitted(so_doc.name):
				so_doc.submit()

			# Cancel Sales order if Zort order status is "Voided"
			if so_doc.zort_order_status == "Voided":
				if so_doc.docstatus == 0:
					so_doc.submit()
				so_doc.cancel()
		print(f"Sales Order {so_doc.name} updated with Zort data.")

	return {"status": "success", "message": _("Sales Order updated successfully.")}

def get_warehouse_from_zort(zort_sales_order_no: str, tracking_no: str, description: str) -> str:
	"""
	Get the warehouse from Zort data.
	This function can be customized to determine the warehouse based on Zort Setting.
	"""
	default_warehouse = get_cached_value("Zort Setting", None, "default_warehouse")
	if not default_warehouse:
		default_warehouse = get_cached_value("Stock Settings", None, "default_warehouse")

	# Check if the Zort sales order number matches the tracking number
	# For Parabola, it means the customer will receive the order at the storefront.
	# Then get warehouse based on description
	if zort_sales_order_no == tracking_no:
		if frappe.db.exists("Warehouse", {"name": description, "is_group": 0}):
			return description

	return default_warehouse

def get_existing_zort_order_ids():
	"""
	Get a list of existing Zort Order IDs from Sales Orders.
	This function retrieves all Sales Orders that have a Zort Order ID.
	"""
	zort_order_ids = [
		int(order_id) for order_id in frappe.db.get_list(
			"Sales Order",
			filters={"zort_order_id": ["!=", ""]},
			pluck="zort_order_id"
		) if order_id.isdigit()
	]
	frappe.logger().info(f"Retrieved Zort Order IDs: {zort_order_ids}")

	return zort_order_ids

def check_if_sales_order_can_be_submitted(so_name: str) -> bool:
	"""
	Check if a Sales Order can be submitted.
	In case zort_sales_order_no is equal to tracking_no, it means the customer will receive the order at the storefront.
	Then we check if the warehouse is set to the storefront warehouse.
	"""

	so_doc = frappe.get_doc("Sales Order", so_name)

	if so_doc.zort_sales_order_no == so_doc.tracking_no and so_doc.docstatus == 0:
		# Warehouse should get from description
		description = so_doc.description.strip()
		warehouse = frappe.db.exists("Warehouse", {"name": description, "is_group": 0})
		if not warehouse:
			return False

	return True

# def check_stock_balance():
# 	data = get_stock_balance(item_code="ACOT-UG-30724", warehouse="051 - Mega - P")
# 	print(data)

# def get_current_stock():
# 	"""
# 	Get the current stock of all items in the default warehouse.
# 	This function retrieves the stock levels for all items in the specified warehouse.
# 	"""
# 	default_warehouse = get_cached_value("Stock Settings", None, "default_warehouse")
# 	if not default_warehouse:
# 		frappe.throw(_("Default warehouse is not set in Stock Settings."))

# 	item_list = frappe.db.get_all(
# 		"Item",
# 		fields=["item_code"],
# 		filters={"sync_with_zort": 1, "is_stock_item": 1},
# 	)
# 	print(item_list, "items to check stock")
# 	print(type(item_list))
# 	# x=2/0

# 	stock_details = frappe.db.get_all(
# 		"Bin",
# 		fields=[
# 			"sum(planned_qty) as planned_qty",
# 			"sum(actual_qty) as actual_qty",
# 			"sum(projected_qty) as projected_qty",
# 			"item_code",
# 		],
# 		filters={"item_code": ["in", [item.item_code for item in item_list]]},
# 		group_by="item_code",
# 	)

# 	print(len(stock_details), "items in stock")
# 	# print(stock_details)
# 	return stock_details

@frappe.whitelist()
def update_item_to_zort(item_code: str):
	"""
	Update an item in Zort.
	This function can be customized to update the item in Zort. If there is no iten on zort, add it to Zort.
	:param item_code: str - The item code to update in Zort.
	"""

	data = frappe.get_doc("Item", item_code)
	if not data:
		print(f"Item {item_code} not found.")
		return {"status": "error", "message": _("Item not found.")}

	sell_price, purchase_price = 0.0, 0.0

	if frappe.db.exists("Item Price", {"item_code": item_code, "price_list": "Standard Selling", "selling": 1}):
		item_price_selling = frappe.get_doc("Item Price", {"item_code": item_code, "price_list": "Standard Selling", "selling": 1})
		sell_price = item_price_selling.price_list_rate

	if frappe.db.exists("Item Price", {"item_code": item_code, "price_list": "Standard Buying", "buying": 1}):
		item_price_buying = frappe.get_doc("Item Price", {"item_code": item_code, "price_list": "Standard Buying", "buying": 1})
		purchase_price = item_price_buying.price_list_rate

	# If item is exists in Zort
	item = call_zort_api.get_products(item_code)
	item_exist_in_zort = bool(item.get("count", 0))

	item_data = {
		"sku": item_code,
		"name": data.item_name,
		"sellprice": sell_price,
		"purchaseprice": purchase_price,
		"unittext": data.stock_uom,
		"sell_vat_status": 0,
		"purchase_vat_status": 0,
		"description": strip_html_tags(data.description) or "",
	}

	if not item_exist_in_zort:
		# Add item to Zort
		res = call_zort_api.add_product(item_data)
		return {"status": "success", "message": _("Item added to Zort successfully.")}
	elif item_exist_in_zort:
		# Update item in Zort
		id = item.get("list", [{}])[0].get("id", 0)
		res = call_zort_api.update_product(id=id, data=item_data)
		return {"status": "success", "message": _("Item updated to Zort successfully.")}

	return {"status": "success", "message": _("Nothing to update to Zort.")}
