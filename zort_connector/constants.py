ZORT_CUSTOM_FIELDS = {
	"Sales Order": [
		{
			"fieldname": "zort_details_tab",
			"fieldtype": "Tab Break",
			"label": "Zort Details",
			"insert_after": "connections_tab",
			"allow_on_submit": 1,
		},
		{
			"fieldname": "zort_order_id",
			"fieldtype": "Data",
			"label": "Zort Order ID",
			"insert_after": "zort_details_tab",
			"allow_on_submit": 1,
		},
		{
			"fieldname": "zort_sales_order_no",
			"fieldtype": "Data",
			"label": "Zort Sales Order No.",
			"insert_after": "zort_order_id",
			"allow_on_submit": 1,
		},
		{
			"fieldname": "zort_sales_channel",
			"fieldtype": "Data",
			"label": "Zort Sales Channel",
			"insert_after": "zort_sales_order_no",
			"allow_on_submit": 1,
		},
		{
			"fieldname": "zort_order_status",
			"fieldtype": "Select",
			"label": "Zort Order Status",
			"options": "\nPending\nSuccess\nVoided\nWaiting\nReturned\nPacked\nShipping\nFailed Shipment",
			"insert_after": "zort_sales_channel",
			"allow_on_submit": 1,
		},
		{
			"fieldname": "payment_status",
			"fieldtype": "Select",
			"label": "Payment Status",
			"options": "\nPending\nPaid\nVoided\nPartial Payment\nExcess Payment",
			"insert_after": "zort_order_status",
			"allow_on_submit": 1,
		},
		{
			"fieldname": "tracking_no",
			"fieldtype": "Data",
			"label": "Tracking No.",
			"insert_after": "payment_status",
			"allow_on_submit": 1,
		},
		{
			"fieldname": "shipping_channel",
			"fieldtype": "Data",
			"label": "Shipping Channel",
			"insert_after": "tracking_no",
			"allow_on_submit": 1,
		},
		{
			"fieldname": "description",
			"fieldtype": "Small Text",
			"label": "Description",
			"insert_after": "shipping_channel",
			"allow_on_submit": 1,
		},
		{
			"fieldname": "zort_data_section",
			"fieldtype": "Section Break",
			"label": "Zort Data",
			"insert_after": "description",
		},
		{
			"fieldname": "zort_api_order_data",
			"fieldtype": "Long Text",
			"label": "API Order Data",
			"insert_after": "zort_data_section",
			"read_only": 1,
			"allow_on_submit": 1,
		},
		{
			"fieldname": "is_order_from_zort",
			"fieldtype": "Check",
			"label": "Is Order from Zort",
			"insert_after": "zort_api_order_data",
			"read_only": 1,
		},
	],
	"Item": [
		{
			"fieldname": "sync_with_zort",
			"fieldtype": "Check",
			"label": "Sync with Zort",
			"insert_after": "is_stock_item",
		},
	],
	"Warehouse": [
		{
			"fieldname": "sync_with_zort",
			"fieldtype": "Check",
			"label": "Sync with Zort",
			"insert_after": "is_rejected_warehouse",
			"depends_on": "eval:doc.is_group == 0",
		}
	],
	"Bin": [
		{
			"fieldname": "reserved_qty_from_zort",
			"fieldtype": "Float",
			"label": "Reserved Qty from Zort",
			"insert_after": "reserved_stock",
			"read_only": 1,
		}
	]
}
