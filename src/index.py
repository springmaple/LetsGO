import util
from firestore import get_firestore_instance
from settings import Settings
from sql import Sql


def _upload_master_data(fs, sql):
    # Stock items
    stocks = {}
    for stock in sql.get_stock_items():
        stocks[stock.code] = stock

    for uom in sql.get_stock_item_uom():
        stocks[uom.code].uom.append(uom)

    for stock_code, stock in stocks.items():
        print(f'Uploading stock {util.esc_key(stock_code)}')
        doc_ref = fs.document(f'data/{COMPANY_CODE}/items/{util.esc_key(stock_code)}')
        doc_ref.set(stock.to_dict())

    # Item groups
    for group in sql.get_stock_groups():
        print(f'Uploading stock group {util.esc_key(group.code)}')
        doc_ref = fs.document(f'data/{COMPANY_CODE}/itemGroups/{util.esc_key(group.code)}')
        doc_ref.set(group.to_dict())

    # Customer
    customers = {}
    for customer in sql.get_customers():
        customers[customer.code] = customer

    for branch in sql.get_customer_branch():
        customers[branch.customer_code].branch.append(branch)

    for customer_code, customer in customers.items():
        print(f'Uploading customer {util.esc_key(customer_code)}')
        doc_ref = fs.document(f'data/{COMPANY_CODE}/customers/{util.esc_key(customer_code)}')
        doc_ref.set(customer.to_dict())

    # Agent
    for agent in sql.get_agents():
        print(f'Uploading agent {util.esc_key(agent.code)}')
        doc_ref = fs.document(f'data/{COMPANY_CODE}/agents/{util.esc_key(agent.code)}')
        doc_ref.set(agent.to_dict())


def _get_sales_orders(fs, sql):
    sync_key = 'created_on'
    for doc in fs.collection(f'data/{COMPANY_CODE}/salesOrders') \
            .where(sync_key, '>', SETTINGS.get_last_sales_order()) \
            .order_by(sync_key) \
            .stream():
        print(f'Syncing sales order {doc.id}')
        sales_order = doc.to_dict()
        sql.set_sales_order(sales_order)

        SETTINGS.set_last_sales_order(sales_order[sync_key])


if __name__ == '__main__':
    SETTINGS = Settings()
    COMPANY_CODE = SETTINGS.get_company_code()

    fs_ = get_firestore_instance()
    with Sql() as sql_:
        sql_.login()
        _get_sales_orders(fs_, sql_)
        _upload_master_data(fs_, sql_)
