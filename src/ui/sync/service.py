import time

import psutil
from google.cloud import firestore

import util
from constants import SalesOrderStatus
from settings import Settings
from sql import StockItem, StockItemGroup, Customer, StockItemUom, CustomerBranch, Agent, Sql
from sql.query import aging_report
from ui import Profile
from ui.view_model import download_cache_items

_LAST_SALES_ORDER_TIMESTAMP = 'last_sales_order_timestamp'
_ST_ITEM_LAST_MODIFIED = 'last_modified_st_item'
_ST_GROUP_LAST_MODIFIED = 'last_modified_st_group'
_ST_CUSTOMER_LAST_MODIFIED = 'last_modified_st_customer'
_ST_TRANS_LAST_TRANS_NO = 'last_trans_no_st_trans'


def is_sql_running() -> bool:
    return "SQLACC.exe" in (p.name() for p in psutil.process_iter())


class SyncService:
    def __init__(self, fs, profile: Profile, settings: Settings, sql: Sql):
        self._fs = fs
        self._sql = sql
        self._profile = profile
        self._company_code = profile.company_code
        self._settings = settings

    def check_login(self):
        self._sql.verify_login(self._profile.company_name)

    def upload_stock_items(self):
        # Stock items
        last_modified = self._settings.get_prop(self._company_code, _ST_ITEM_LAST_MODIFIED) or None
        table_name = 'ST_ITEM'
        uom_table_name = 'ST_ITEM_UOM'
        total = self._sql.count_master_data(table_name, last_modified)
        item_code_updated = set()
        for stock in self._sql.get_master_data(table_name, total, lambda data: StockItem(data), last_modified):
            stock_code = stock.code
            stock.uom = list(self._sql.get_master_detail_by_code(
                uom_table_name, stock_code, lambda data: StockItemUom(data)))
            doc_ref = self._fs.document(f'data/{self._company_code}/items/{util.esc_key(stock_code)}')
            doc_ref.set(stock.to_dict())

            if util.is_last_modified_not_empty(stock.last_modified):
                self._settings.set_prop(self._company_code, _ST_ITEM_LAST_MODIFIED, stock.last_modified)
            item_code_updated.add(stock.code)

        last_trans_no = self._settings.get_prop(self._company_code, _ST_TRANS_LAST_TRANS_NO) or None
        stock_trans_to_update = []
        for stock_trans in self._sql.get_st_trans(last_trans_no):
            should_update = stock_trans.item_code not in item_code_updated
            stock_trans_to_update.append((stock_trans, should_update))
            item_code_updated.add(stock_trans.item_code)

        for stock_trans, should_update in stock_trans_to_update:
            if should_update:
                stock = self._sql.get_master_data_by_code(table_name, stock_trans.item_code,
                                                          lambda data: StockItem(data))
                stock_code = stock.code
                stock.uom = list(self._sql.get_master_detail_by_code(
                    uom_table_name, stock_code, lambda data: StockItemUom(data)))
                doc_ref = self._fs.document(f'data/{self._company_code}/items/{util.esc_key(stock_code)}')
                doc_ref.set(stock.to_dict())
                yield stock
            self._settings.set_prop(self._company_code, _ST_TRANS_LAST_TRANS_NO, stock_trans.trans_no)

    def upload_item_groups(self):
        # Item groups
        last_modified = self._settings.get_prop(self._company_code, _ST_GROUP_LAST_MODIFIED) or None
        table_name = 'ST_GROUP'
        total = self._sql.count_master_data(table_name, last_modified)
        for group in self._sql.get_master_data(table_name, total, lambda data: StockItemGroup(data), last_modified):
            doc_ref = self._fs.document(f'data/{self._company_code}/itemGroups/{util.esc_key(group.code)}')
            doc_ref.set(group.to_dict())
            if util.is_last_modified_not_empty(group.last_modified):
                self._settings.set_prop(self._company_code, _ST_GROUP_LAST_MODIFIED, group.last_modified)
            yield group

    def upload_customers(self):
        # Customer
        last_modified = self._settings.get_prop(self._company_code, _ST_CUSTOMER_LAST_MODIFIED) or None
        table_name = 'AR_CUSTOMER'
        branch_table_name = 'AR_CUSTOMERBRANCH'
        total = self._sql.count_master_data(table_name, last_modified)
        for customer in self._sql.get_master_data(table_name, total, lambda data: Customer(data), last_modified):
            customer_code = customer.code
            customer.branch = list(self._sql.get_master_detail_by_code(
                branch_table_name, customer_code, lambda data: CustomerBranch(data)))
            doc_ref = self._fs.document(f'data/{self._company_code}/customers/{util.esc_key(customer_code)}')
            doc_ref.set(customer.to_dict())
            if util.is_last_modified_not_empty(customer.last_modified):
                self._settings.set_prop(self._company_code, _ST_CUSTOMER_LAST_MODIFIED, customer.last_modified)
            yield customer

    def upload_agents(self):
        # Agent
        table_name = 'AGENT'
        total = self._sql.count_master_data(table_name)
        for agent in self._sql.get_master_data(table_name, total, lambda data: Agent(data),
                                               order_by_last_modified=False):
            doc_ref = self._fs.document(f'data/{self._company_code}/agents/{util.esc_key(agent.code)}')
            doc_ref.set(agent.to_dict())
            yield agent

    def sync_sales_orders(self):

        def _get_item_quantities(items):
            result = {}
            for item in items:
                item_code = util.esc_key(item['item']['code'])
                item_quantity = item['quantity'] * int(item['uom']['rate'])
                if item_code not in result:
                    result[item_code] = 0
                result[item_code] += item_quantity
            return result

        @firestore.transactional
        def _update(transaction, so_code, so_dict):
            item_quantities = _get_item_quantities(so_dict['items'])
            to_save = []
            for item_code, item_quantity in item_quantities.items():
                item_doc = self._fs.document(f'data/{self._company_code}/itemQuantities/{item_code}')
                current_quantity = 0
                item_quantity_dict = item_doc.get(transaction=transaction).to_dict()
                if item_quantity_dict:
                    current_quantity = item_quantity_dict['open']
                current_quantity -= item_quantity
                to_save.append((item_doc, {'open': current_quantity}))

            for item_doc, item_data in to_save:
                transaction.set(item_doc, item_data)

            so_ref = self._fs.document(f'data/{self._company_code}/salesOrders/{so_code}')
            transaction.set(so_ref, so_dict)

        collection = f'data/{self._company_code}/salesOrders'
        for doc in self._fs.collection(collection).where('status', '==', SalesOrderStatus.Open.value).stream():
            sales_order_dict = doc.to_dict()
            try:
                self._sql.set_sales_order(sales_order_dict)
            except Exception as ex:
                if 'attempt to store duplicate value' in str(ex):
                    sales_order_code = sales_order_dict['code']
                    sales_order = self._sql.get_sl_so(sales_order_code)
                    if sales_order and sales_order.is_cancelled:
                        sales_order_dict['status'] = SalesOrderStatus.Cancelled.value
                        _update(self._fs.transaction(), sales_order_code, sales_order_dict)
                        yield sales_order_dict
                        continue
                    outstanding_sales_order = self._sql.get_outstanding_so(sales_order_code)
                    if outstanding_sales_order:
                        sales_order_dict['status'] = SalesOrderStatus.Transferred.value
                        _update(self._fs.transaction(), sales_order_code, sales_order_dict)
                    yield sales_order_dict
                    continue
                raise
            else:
                yield sales_order_dict

    def upload_aging_report(self):
        collection = f'data/{self._company_code}'
        doc = self._fs.document(collection)

        rpt_docs = []
        for index, rpt_doc in enumerate(aging_report.get_aging_report(self._sql), start=1):
            rpt_docs.append(rpt_doc.to_dict())
            yield rpt_doc
        doc.set({
            'aging_report': {
                'updated_on': time.time(),
                'documents': rpt_docs
            }
        }, merge=True)

    def update_cache(self):
        yield from download_cache_items(self._company_code, self._fs)
