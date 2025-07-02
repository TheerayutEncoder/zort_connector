import frappe
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder
from erpnext.stock.stock_balance import update_bin_qty

from zort_connector.custom.stock_balance import get_reserved_qty_from_zort

class SalesOrderZort(SalesOrder):

	def on_submit(self):
		super().on_submit()
		self.update_reserved_qty_from_zort()

	def on_cancel(self):
		super().on_cancel()
		self.update_reserved_qty_from_zort()

	def update_status(self):
		super().update_status()
		self.update_reserved_qty_from_zort()

	def update_reserved_qty_from_zort(self, so_item_rows=None):
		"""update reserved qty from zort for sales order which is_order_from_zort is 1"""
		item_wh_list = []

		def _valid_for_reserve(item_code, warehouse):
			if (
				item_code
				and warehouse
				and [item_code, warehouse] not in item_wh_list
				and frappe.get_cached_value("Item", item_code, "is_stock_item")
			):
				item_wh_list.append([item_code, warehouse])

		if self.is_order_from_zort:
			for d in self.get("items"):
				if (not so_item_rows or d.name in so_item_rows) and not d.delivered_by_supplier:
					if self.has_product_bundle(d.item_code):
						for p in self.get("packed_items"):
							if p.parent_detail_docname == d.name and p.parent_item == d.item_code:
								_valid_for_reserve(p.item_code, p.warehouse)
					else:
						_valid_for_reserve(d.item_code, d.warehouse)
		for item_code, warehouse in item_wh_list:
			print("get_reserve_qty_from_zort", get_reserved_qty_from_zort(item_code, warehouse))
			update_bin_qty(item_code, warehouse, {"reserved_qty_from_zort": get_reserved_qty_from_zort(item_code, warehouse)})
