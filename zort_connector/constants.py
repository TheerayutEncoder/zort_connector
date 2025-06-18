ZORT_CUSTOM_FIELDS = {
	"Sales Order": [
		{
			"fieldname": "zort_details_tab",
			"fieldtype": "Tab Break",
			"label": "Zort Details",
			"insert_after": "connections_tab",
		},
		{
			"fieldname": "zort_order_id",
			"fieldtype": "Data",
			"label": "Zort Order ID",
			"insert_after": "zort_details_tab",
		},
		{
			"fieldname": "zort_sales_order_no",
			"fieldtype": "Data",
			"label": "Zort Sales Order No.",
			"insert_after": "zort_order_id",
		},
		{
			"fieldname": "zort_sales_channel",
			"fieldtype": "Data",
			"label": "Zort Sales Channel",
			"insert_after": "zort_sales_order_no",
		},
		{
			"fieldname": "zort_order_status",
			"fieldtype": "Select",
			"label": "Zort Order Status",
			"options": "\nPending\nSuccess\nVoided\nWaiting\nReturned\nPacked\nShipping\nFailed Shipment",
			"insert_after": "zort_sales_channel",
		},
		{
			"fieldname": "payment_status",
			"fieldtype": "Select",
			"label": "Payment Status",
			"options": "\nPending\nPaid\nVoided\nPartial Payment\nExcess Payment",
			"insert_after": "zort_order_status",
		},
		{
			"fieldname": "tracking_no",
			"fieldtype": "Date",
			"label": "Tracking No.",
			"insert_after": "payment_status",
		},
		{
			"fieldname": "sales_channel",
			"fieldtype": "Data",
			"label": "Sales Channel",
			"insert_after": "tracking_no",
		}
	]
}
