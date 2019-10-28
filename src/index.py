import time
import traceback

from tqdm import tqdm

import util
from firestore import get_firestore_instance
from settings import Settings
from sql import Sql, StockItem, StockItemGroup, Customer, StockItemUom, CustomerBranch, Agent
from sql.query import aging_report

_LAST_SALES_ORDER_TIMESTAMP = 'last_sales_order_timestamp'
_ST_ITEM_LAST_MODIFIED = 'last_modified_st_item'
_ST_GROUP_LAST_MODIFIED = 'last_modified_st_group'
_ST_TRANS_LAST_TRANS_NO = 'last_trans_no_st_trans'


def _upload_master_data(fs, sql: Sql, company_code: str, settings: Settings):
    # Stock items
    last_modified = settings.get_prop(company_code, _ST_ITEM_LAST_MODIFIED) or None
    table_name = 'ST_ITEM'
    uom_table_name = 'ST_ITEM_UOM'
    total = sql.count_master_data(table_name, last_modified)
    item_code_updated = set()
    with tqdm(total=total, desc='Stock Items', unit='Item') as progress:
        for stock in sql.get_master_data(table_name, total, lambda data: StockItem(data), last_modified):
            stock_code = stock.code
            stock.uom = list(sql.get_master_detail_by_code(
                uom_table_name, stock_code, lambda data: StockItemUom(data)))
            doc_ref = fs.document(f'data/{company_code}/items/{util.esc_key(stock_code)}')
            doc_ref.set(stock.to_dict())

            if util.is_last_modified_not_empty(stock.last_modified):
                settings.set_prop(company_code, _ST_ITEM_LAST_MODIFIED, stock.last_modified)
            item_code_updated.add(stock.code)

            progress.update(1)

        last_trans_no = settings.get_prop(company_code, _ST_TRANS_LAST_TRANS_NO) or None
        stock_trans_to_update = []
        for stock_trans in sql.get_st_trans(last_trans_no):
            should_update = stock_trans.item_code not in item_code_updated
            stock_trans_to_update.append((stock_trans, should_update))
            item_code_updated.add(stock_trans.item_code)

        progress.total = total + len(list(filter(lambda i: i[1], stock_trans_to_update)))
        progress.set_postfix(refresh=False)
        progress.update(0)

        for stock_trans, should_update in stock_trans_to_update:
            if should_update:
                stock = sql.get_master_data_by_code(table_name, stock_trans.item_code,
                                                    lambda data: StockItem(data))
                stock_code = stock.code
                stock.uom = list(sql.get_master_detail_by_code(
                    uom_table_name, stock_code, lambda data: StockItemUom(data)))
                doc_ref = fs.document(f'data/{company_code}/items/{util.esc_key(stock_code)}')
                doc_ref.set(stock.to_dict())
                progress.update(1)
            settings.set_prop(company_code, _ST_TRANS_LAST_TRANS_NO, stock_trans.trans_no)

    # Item groups
    last_modified = settings.get_prop(company_code, _ST_GROUP_LAST_MODIFIED) or None
    table_name = 'ST_GROUP'
    total = sql.count_master_data(table_name, last_modified)
    with tqdm(total=total, desc='Stock Groups', unit='Group') as progress:
        for group in sql.get_master_data(table_name, total, lambda data: StockItemGroup(data), last_modified):
            doc_ref = fs.document(f'data/{company_code}/itemGroups/{util.esc_key(group.code)}')
            doc_ref.set(group.to_dict())
            if util.is_last_modified_not_empty(group.last_modified):
                settings.set_prop(company_code, _ST_GROUP_LAST_MODIFIED, group.last_modified)
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
        for agent in sql.get_master_data(table_name, total, lambda data: Agent(data), order_by_last_modified=False):
            doc_ref = fs.document(f'data/{company_code}/agents/{util.esc_key(agent.code)}')
            doc_ref.set(agent.to_dict())
            progress.update(1)


def _get_sales_orders(fs, sql: Sql, company_code: str, settings: Settings):
    collection = f'data/{company_code}/salesOrders'
    sync_key = 'created_on'
    sync_since = settings.get_prop(company_code, _LAST_SALES_ORDER_TIMESTAMP)

    def save_checkpoint():
        settings.set_prop(company_code, _LAST_SALES_ORDER_TIMESTAMP, sales_order[sync_key])

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
                'updated_on': time.time(),
                'documents': rpt_docs
            }
        }, merge=True)


def start():
    settings = Settings()
    fs = get_firestore_instance()
    for company_code in settings.list_company_codes():
        with Sql(settings.get_sql_credential(company_code)) as sql:
            print(f'Synchronizing "{company_code}"')
            _get_sales_orders(fs, sql, company_code, settings)
            _upload_master_data(fs, sql, company_code, settings)
            _get_aging_reports(fs, sql, company_code)


if __name__ == '__main__':
    try:
        start()
        print('OK...')
    except:
        traceback.print_exc()
        print('ERROR...')
