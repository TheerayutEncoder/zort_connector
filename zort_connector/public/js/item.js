frappe.ui.form.on('Item', {
	refresh: function(frm) {
		if (frm.doc.sync_with_zort) {
			frm.add_custom_button(
				__("Update item to Zort"),
				function () {
					frm.trigger("update_item_to_zort");
				},
				__("Actions")
			);
		}
	},

	update_item_to_zort: function(frm) {
		frappe.call({
			method: "zort_connector.api.custom_api.update_item_to_zort",
			args: {
				item_code: frm.doc.name
			},
			callback: function(r) {
				if (r.message && r.message.status === "success") {
					frappe.show_alert({
						message: __("{0}", [r.message.message]),
						indicator: 'green'
					});
				} else {
					frappe.show_alert({
						message: __("Failed to add/update item to Zort."),
						indicator: 'red'
					});
				}
			}
		});
	}
});
