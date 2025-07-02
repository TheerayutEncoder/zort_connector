import frappe
from frappe.utils import flt

from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum, Coalesce


def get_reserved_qty_from_zort(item_code, warehouse):
	"""
	Get the reserved quantity for an item in a specific warehouse from Zort.
	"""
	if not item_code or not warehouse:
		return 0.0

	SalesOrder = DocType("Sales Order")
	SalesOrderItem = DocType("Sales Order Item")
	PackedItem = DocType("Packed Item")

	query = (
		frappe.qb.from_(SalesOrder)
		.left_join(SalesOrderItem)
			.on((SalesOrder.name == SalesOrderItem.parent) &
				(SalesOrderItem.item_code == item_code) &
				(SalesOrderItem.warehouse == warehouse))
		.left_join(PackedItem)
			.on((SalesOrder.name == PackedItem.parent) &
				(PackedItem.parenttype == "Sales Order") &
				(PackedItem.item_code != PackedItem.parent_item) &
				(PackedItem.item_code == item_code) &
				(PackedItem.warehouse == warehouse))
		.select(
			(Coalesce(Sum(SalesOrderItem.qty), 0) + Coalesce(Sum(PackedItem.qty), 0)).as_("total_reserved_qty")
		)
		.where(
			(SalesOrder.is_order_from_zort == 1) &
			(SalesOrder.docstatus == 1) &
			(SalesOrder.status != "Completed")
		)
	)
	reserved_qty_from_zort = query.run(as_dict=True)
	print("Reserved Qty from Zort:", reserved_qty_from_zort)
	return flt(reserved_qty_from_zort[0].get("total_reserved_qty", 0)) if reserved_qty_from_zort else 0.0
