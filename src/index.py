from firestore import get_firestore_instance
from sql import Sql

COMPANY_CODE = 'test'


def _escape_key(key: str):
    return key.replace('/', '_')


def _upload_master_data(fs, sql):
    # Stock items
    stocks = {}
    for stock in sql.get_stock_items():
        stocks[stock.code] = stock

    for uom in sql.get_stock_item_uom():
        stocks[uom.code].uom.append(uom)

    for stock_code, stock in stocks.items():
        print(f'Uploading stock {_escape_key(stock_code)}')
        doc_ref = fs.document(f'data/{COMPANY_CODE}/items/{_escape_key(stock_code)}')
        doc_ref.set(stock.to_dict())

    # Item groups
    for group in sql.get_stock_groups():
        print(f'Uploading stock group {_escape_key(group.code)}')
        doc_ref = fs.document(f'data/{COMPANY_CODE}/itemGroups/{_escape_key(group.code)}')
        doc_ref.set(group.to_dict())

    # Customer
    customers = {}
    for customer in sql.get_customers():
        customers[customer.code] = customer

    for branch in sql.get_customer_branch():
        customers[branch.customer_code].branch.append(branch)

    for customer_code, customer in customers.items():
        print(f'Uploading customer {_escape_key(customer_code)}')
        doc_ref = fs.document(f'data/{COMPANY_CODE}/customers/{_escape_key(customer_code)}')
        doc_ref.set(customer.to_dict())

    # Agent
    for agent in sql.get_agents():
        print(f'Uploading agent {_escape_key(agent.code)}')
        doc_ref = fs.document(f'data/{COMPANY_CODE}/agents/{_escape_key(agent.code)}')
        doc_ref.set(agent.to_dict())


def upload_master_data():
    fs = get_firestore_instance()
    with Sql() as sql:
        sql.login()
        _upload_master_data(fs, sql)


def _get_sales_orders(fs):
    with Sql() as sql:
        for doc in fs.collection(f'data/{COMPANY_CODE}/salesOrders').stream():
            print(f'Syncing sales order {doc.id}')
            sql.login()
            sql.set_sales_order(doc.to_dict())


# upload_master_data()
_get_sales_orders(get_firestore_instance())
