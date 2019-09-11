import firebase_admin
from firebase_admin import credentials, firestore

from sql import Sql


def _escape_key(key: str):
    return key.replace('/', '_')


def start():
    cred = credentials.Certificate('../res/serviceAccount.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    # Stock items
    stocks = {}
    for stock in sql.get_stock_items():
        stocks[stock.code] = stock

    for uom in sql.get_stock_item_uom():
        stocks[uom.code].uom.append(uom)

    for stock_code, stock in stocks.items():
        print(f'Uploading stock {_escape_key(stock_code)}')
        doc_ref = db.document(f'items/{_escape_key(stock_code)}')
        doc_ref.set(stock.to_dict())

    # Item groups
    for group in sql.get_stock_groups():
        print(f'Uploading stock group {_escape_key(group.code)}')
        doc_ref = db.document(f'itemGroups/{_escape_key(group.code)}')
        doc_ref.set(group.to_dict())

    # Customer
    customers = {}
    for customer in sql.get_customers():
        customers[customer.code] = customer

    for branch in sql.get_customer_branch():
        customers[branch.customer_code].branch.append(branch)

    for customer_code, customer in customers.items():
        print(f'Uploading customer {_escape_key(customer_code)}')
        doc_ref = db.document(f'customers/{_escape_key(customer_code)}')
        doc_ref.set(customer.to_dict())


with Sql() as sql:
    sql.login()
    start()
