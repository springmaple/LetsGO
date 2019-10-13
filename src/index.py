import traceback

import util
from firestore import get_firestore_instance
from settings import Settings
from sql import Sql

_LAST_SALES_ORDER_TIMESTAMP = 'last_sales_order_timestamp'
_LAST_STOCK_GROUP_TIMESTAMP = 'last_stock_group_timestamp'


def _upload_master_data(fs, sql: Sql, company_code: str, settings: Settings):
    # Stock items
    stocks = {}
    for stock in sql.get_stock_items(since=0):  # Updating UOM will not reflect on LASTMODIFIED
        stocks[stock.code] = stock
        for uom in sql.get_stock_item_uom(stock.code):
            stock.uom.append(uom)

    for stock_code, stock in stocks.items():
        doc_ref = fs.document(f'data/{company_code}/items/{util.esc_key(stock_code)}')
        doc_ref.set(stock.to_dict())
        print(f'Uploaded stock {util.esc_key(stock_code)}')

    # Item groups
    for group in sql.get_stock_groups(settings.get_last_sync_prop(company_code, _LAST_STOCK_GROUP_TIMESTAMP)):
        doc_ref = fs.document(f'data/{company_code}/itemGroups/{util.esc_key(group.code)}')
        doc_ref.set(group.to_dict())
        settings.set_last_sync_prop(company_code, _LAST_STOCK_GROUP_TIMESTAMP, group.last_modified)
        settings.save()
        print(f'Uploaded stock group {util.esc_key(group.code)}')

    # Customer
    customers = {}
    for customer in sql.get_customers(since=0):  # Updating branch will not reflect on LASTMODIFIED
        customers[customer.code] = customer
        for branch in sql.get_customer_branch(customer.code):
            customer.branch.append(branch)

    for customer_code, customer in customers.items():
        doc_ref = fs.document(f'data/{company_code}/customers/{util.esc_key(customer_code)}')
        doc_ref.set(customer.to_dict())
        print(f'Uploaded customer {util.esc_key(customer_code)}')

    # Agent
    for agent in sql.get_agents():
        doc_ref = fs.document(f'data/{company_code}/agents/{util.esc_key(agent.code)}')
        doc_ref.set(agent.to_dict())
        print(f'Uploaded agent {util.esc_key(agent.code)}')


def _get_sales_orders(fs, sql: Sql, company_code: str, settings: Settings):
    def save_checkpoint():
        settings.set_last_sync_prop(company_code, _LAST_SALES_ORDER_TIMESTAMP, sales_order[sync_key])
        settings.save()

    sync_key = 'created_on'

    for doc in fs.collection(f'data/{company_code}/salesOrders') \
            .where(sync_key, '>', settings.get_last_sync_prop(company_code, _LAST_SALES_ORDER_TIMESTAMP)) \
            .order_by(sync_key) \
            .stream():
        sales_order = doc.to_dict()
        try:
            sql.set_sales_order(sales_order)
        except Exception as ex:
            if "attempt to store duplicate value" in str(ex):
                save_checkpoint()
                print(f'Skipped sales order {doc.id}')
                continue
            raise
        else:
            save_checkpoint()
            print(f'Downloaded sales order {doc.id}')


def start():
    settings = Settings()
    fs = get_firestore_instance()
    for company_code in settings.list_company_codes():
        with Sql(settings.get_sql_credential(company_code)) as sql:
            print(f'Switching to company "{company_code}"')
            sql.login()
            _get_sales_orders(fs, sql, company_code, settings)
            _upload_master_data(fs, sql, company_code, settings)


if __name__ == '__main__':
    try:
        start()
    except:
        traceback.print_exc()
