### Zort Connector

Connect Zort with ERPNext

<img width="1305" height="452" alt="Selection_579" src="https://github.com/user-attachments/assets/72ad1f7e-641e-43e0-9ab3-8ec540b37770" />


### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app zort_connector
```
### Configuration

1. Go to `Zort setting` doctype
2. Fill data to connect with Zort (You can get this data by going to your [Zort Account](https://secure.zortout.com/Home/LogOn))
   
   2.1 Zort Endpoint URL
   
   2.2 Storename
   
   2.3 apikey
   
   2.4 apisecret
   
   2.5 Default Warehouse (Use for erpnext to consider, which warehouse should be use to create sales order)
   
<img width="1792" height="652" alt="Selection_578" src="https://github.com/user-attachments/assets/5c182a31-f2ee-42d2-8900-33e0169026d4" />

### Features

1. Add item from ERPNext to Zort (by enable `Sync with zort`)
<img width="1781" height="620" alt="Selection_581" src="https://github.com/user-attachments/assets/e277c70e-61a1-4cac-904c-07f6756924f9" />

2. Every pending sales order on Zort will be created and updated (if the status on zort has changed) in ERPnext (Using scheduled tasks)

on path `/zort_connector/hooks.py`
```python
# Scheduled Tasks
# ---------------
scheduler_events = {
    "all": [
        "frappe.email.queue.flush"  # This triggers the scheduler engine
    ],
    "cron": {
        "5 * * * *": [
            "zort_connector.api.custom_api.create_sales_order_from_zort",
            "zort_connector.api.custom_api.update_sales_order_from_zort"
        ]
    },
}
```

For test create sales order from Zort, you can use the bench command, for example:

```bash
bench --site yoursite.local execute zort_connector.api.custom_api.create_sales_order_from_zort
```

3. Create new customer if customer does not exist in ERPNext (At this time we check by using phone number)

4. For real time stock we need know how many items have been reserved from Zort or on ERPNext (before custom, it includes together on reserve Qty inside `Bin doctype`), so we create a new field to save the reserve qty from Zort.
   <img width="1624" height="477" alt="image" src="https://github.com/user-attachments/assets/cbc6782a-366e-4f91-a1ac-2f61fed0379f" />

**Note: Actually, this is not a standard implementation for integration with Zort (work in progress)**

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/zort_connector
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit

### More information about Zort

- [API documentation](https://developers.zortout.com/)
- Line 
