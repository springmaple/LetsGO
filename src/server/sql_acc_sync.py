import time

import psutil
from google.cloud import firestore

from constants import SalesOrderStatus
from firestore import get_firestore_instance
from server import Profile, util
from settings import Settings
from sql import StockItem, StockItemUom, StockItemGroup, Customer, CustomerBranch, Agent, Sql
from sql.query import aging_report

_LAST_SYNC_SQL_TIMESTAMP = 'last_sync_sql_timestamp'
_LAST_SALES_ORDER_TIMESTAMP = 'last_sales_order_timestamp'
_ST_ITEM_LAST_MODIFIED = 'last_modified_st_item'
_ST_GROUP_LAST_MODIFIED = 'last_modified_st_group'
_ST_CUSTOMER_LAST_MODIFIED = 'last_modified_st_customer'
_ST_TRANS_LAST_TRANS_NO = 'last_trans_no_st_trans'


def _is_sql_acc_running() -> bool:
    return "SQLACC.exe" in (p.info['name'] for p in psutil.process_iter(['name']))


class SqlAccSynchronizer:
    def __init__(self, company_code):
        self.company_code = company_code

    def start_sync(self):
        if not _is_sql_acc_running():
            raise Exception('Please start SQL Account and login first.')

        fs = get_firestore_instance()
        settings = Settings()
        profile = settings.get_profile(self.company_code)  # type: Profile

        with Sql() as sql:
            ss = _SyncService(fs, profile, settings, sql)
            ss.check_login()

            for item in ss.upload_stock_items():
                yield {'type': 'item', 'item': item.to_dict()}

            for item_code in ss.delete_stock_items():
                yield {'type': 'delete_item', 'deleted_item_code': item_code}

            for item_group in ss.upload_item_groups():
                yield {'type': 'item_group', 'item_group': item_group.to_dict()}

            for customer in ss.upload_customers():
                yield {'type': 'customer', 'customer': customer.to_dict()}

            for agent in ss.upload_agents():
                yield {'type': 'agent', 'agent': agent.to_dict()}

            for update in ss.sync_sales_orders():
                # update: added, transferred, cancelled, nochange
                if type(update) != str:
                    yield {'type': 'sales_order', 'sales_order': update}

            yield {'type': 'aging_report', 'aging_report': 'Started!'}
            ss.upload_aging_report()
            yield {'type': 'aging_report', 'aging_report': 'Completed!'}

        settings.set_prop(self.company_code, _LAST_SYNC_SQL_TIMESTAMP, int(time.time()))


class _SyncService:
    def __init__(self, fs, profile: Profile, settings: Settings, sql: Sql):
        self._fs = fs
        self._profile = profile
        self._settings = settings
        self._sql = sql
        self._company_code = profile.company_code

    def check_login(self):
        self._sql.verify_login(self._profile.company_name)

    def upload_stock_items(self):
        # Stock items
        def upload_stock_item(stock_):
            stock_code = stock_.code
            stock_.uom = list(self._sql.get_master_detail_by_code(
                uom_table_name, stock_code, lambda data: StockItemUom(data)))
            doc_ref = self._fs.document(f'data/{self._company_code}/items/{util.esc_key(stock_code)}')
            doc_ref.set(stock_.to_dict())
            return stock_

        last_modified = self._settings.get_prop(self._company_code, _ST_ITEM_LAST_MODIFIED) or None
        table_name = 'ST_ITEM'
        uom_table_name = 'ST_ITEM_UOM'
        total = self._sql.count_master_data(table_name, last_modified)
        item_code_updated = set()
        for stock in self._sql.get_master_data(table_name, total, lambda data: StockItem(data), last_modified):
            yield upload_stock_item(stock)

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
                yield upload_stock_item(stock)
            self._settings.set_prop(self._company_code, _ST_TRANS_LAST_TRANS_NO, stock_trans.trans_no)

    def delete_stock_items(self):
        # Delete stock items that already removed in SQL from server.
        active_stock_item_codes = set(map(lambda code: util.esc_key(code), self._sql.get_stock_item_codes()))
        server_item_codes = [doc.id for doc in self._fs.collection(f'data/{self._company_code}/items').stream()]
        for server_item_code in server_item_codes:
            if server_item_code not in active_stock_item_codes:
                self._fs.document(f'data/{self._company_code}/items/{server_item_code}').delete()
                yield server_item_code

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

        with open('sales_order_log.txt', mode='w') as log:
            collection = f'data/{self._company_code}/salesOrders'
            all_docs = [doc.to_dict() for doc in self._fs.collection(collection).where(
                'status', '==', SalesOrderStatus.Open.value).order_by('created_on').stream()]
            print(collection, "total", len(all_docs), file=log)
            for sales_order_dict in all_docs:
                sales_order_code = sales_order_dict['code']
                print('Server:', sales_order_code, file=log)
                yield sales_order_dict

                sales_order = self._sql.get_sl_so(sales_order_code)
                if sales_order:
                    if sales_order.is_cancelled:
                        sales_order_dict['status'] = SalesOrderStatus.Cancelled.value
                        _update(self._fs.transaction(), sales_order_code, sales_order_dict)
                        print('Cancelled', file=log)
                        yield 'cancelled'
                        continue
                    else:
                        outstanding_sales_order = self._sql.get_sl_invoice_dtl(sales_order_code)
                        if outstanding_sales_order:
                            sales_order_dict['status'] = SalesOrderStatus.Transferred.value
                            _update(self._fs.transaction(), sales_order_code, sales_order_dict)
                            print('Transferred', file=log)
                            yield 'transferred'
                            continue
                        print('NoChange', file=log)
                        yield 'nochange'
                        continue
                else:
                    self._sql.set_sales_order(sales_order_dict)
                    print('New', file=log)
                    yield 'added'
                    continue

    def upload_aging_report(self):
        collection = f'data/{self._company_code}'
        doc = self._fs.document(collection)

        rpt_docs = [rpt_doc.to_dict() for rpt_doc in aging_report.get_aging_report(self._sql)]
        doc.set({
            'aging_report': {
                'updated_on': time.time(),
                'documents': rpt_docs
            }
        }, merge=True)
