import traceback

from tqdm import tqdm

import util
from firestore import get_firestore_instance
from settings import Settings
from sql import Sql, StockItem, StockItemGroup, Customer, StockItemUom, CustomerBranch, Agent
from sql.query import aging_report

_LAST_SALES_ORDER_TIMESTAMP = 'last_sales_order_timestamp'


def _upload_master_data(fs, sql: Sql, company_code: str):
    # Stock items
    table_name = 'ST_ITEM'
    uom_table_name = 'ST_ITEM_UOM'
    total = sql.count_master_data(table_name)
    with tqdm(total=total, desc='Stock Items', unit='Item') as progress:
        for stock in sql.get_master_data(table_name, total, lambda data: StockItem(data)):
            stock_code = stock.code
            stock.uom = list(sql.get_master_detail_by_code(
                uom_table_name, stock_code, lambda data: StockItemUom(data)))
            doc_ref = fs.document(f'data/{company_code}/items/{util.esc_key(stock_code)}')
            doc_ref.set(stock.to_dict())
            progress.update(1)

    # Item groups
    table_name = 'ST_GROUP'
    total = sql.count_master_data(table_name)
    with tqdm(total=total, desc='Stock Groups', unit='Group') as progress:
        for group in sql.get_master_data(table_name, total, lambda data: StockItemGroup(data)):
            doc_ref = fs.document(f'data/{company_code}/itemGroups/{util.esc_key(group.code)}')
            doc_ref.set(group.to_dict())
            progress.update(1)

    # Customer
    table_name = 'AR_CUSTOMER'
    branch_table_name = 'AR_CUSTOMERBRANCH'
    total = sql.count_master_data(table_name)
    with tqdm(total=total, desc='Customers', unit='Customer') as progress:
        for customer in sql.get_master_data(table_name, total, lambda data: Customer(data)):
            customer_code = customer.code
            customer.branch = list(sql.get_master_detail_by_code(
                branch_table_name, customer_code, lambda data: CustomerBranch(data)))
            doc_ref = fs.document(f'data/{company_code}/customers/{util.esc_key(customer_code)}')
            doc_ref.set(customer.to_dict())
            progress.update(1)

    # Agent
    table_name = 'AGENT'
    total = sql.count_master_data(table_name)
    with tqdm(total=total, desc='Agents', unit='Agent') as progress:
        for agent in sql.get_master_data(table_name, total, lambda data: Agent(data)):
            doc_ref = fs.document(f'data/{company_code}/agents/{util.esc_key(agent.code)}')
            doc_ref.set(agent.to_dict())
            progress.update(1)


def _get_sales_orders(fs, sql: Sql, company_code: str, settings: Settings):
    def save_checkpoint():
        settings.set_last_sync_prop(company_code, _LAST_SALES_ORDER_TIMESTAMP, sales_order[sync_key])
        settings.save()

    collection = f'data/{company_code}/salesOrders'
    sync_key = 'created_on'
    sync_since = settings.get_last_sync_prop(company_code, _LAST_SALES_ORDER_TIMESTAMP)

    with tqdm(total=0, desc='Sales Order', unit='Sales Order') as progress:
        for index, doc in enumerate(
                fs.collection(collection).where(sync_key, '>', sync_since).order_by(sync_key).stream(), start=1):
            progress.total = index
            progress.set_postfix(refresh=False)
            progress.update(0)
            sales_order = doc.to_dict()
            try:
                sql.set_sales_order(sales_order)
            except Exception as ex:
                if 'attempt to store duplicate value' in str(ex):
                    save_checkpoint()
                    progress.update(1)
                    continue
                raise
            else:
                save_checkpoint()
                progress.update(1)


def _get_aging_reports(fs, sql: Sql, company_code: str):
    collection = f'data/{company_code}'
    doc = fs.document(collection)

    with tqdm(total=0, desc='Aging Report', unit='Document') as progress:
        rpt_docs = []
        for index, rpt_doc in enumerate(aging_report.get_aging_report(sql), start=1):
            progress.total = index
            progress.set_postfix(refresh=False)
            progress.update(0)
            rpt_docs.append(rpt_doc.to_dict())
            progress.update(1)
        doc.set({
            'aging_report': {
                'updated_on': 0,
                'documents': rpt_docs
            }
        }, merge=True)


def start():
    settings = Settings()
    fs = get_firestore_instance()
    for company_code in settings.list_company_codes():
        with Sql(settings.get_sql_credential(company_code)) as sql:
            print(f'Synchronizing "{company_code}"')
            sql.login()
            _get_sales_orders(fs, sql, company_code, settings)
            _upload_master_data(fs, sql, company_code)
            _get_aging_reports(fs, sql, company_code)


if __name__ == '__main__':
    try:
        start()
        print('OK...')
    except:
        traceback.print_exc()
        print('ERROR...')
