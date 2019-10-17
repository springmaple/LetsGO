from datetime import datetime, timedelta, tzinfo
from decimal import Decimal

import win32com.client

from sql import util
from sql.master import Total
from sql.master.agent import Agent
from sql.master.customer import Customer
from sql.master.customer_branch import CustomerBranch
from sql.master.stock_item import StockItem
from sql.master.stock_item_group import StockItemGroup
from sql.master.stock_item_uom import StockItemUom

_LOAD_MASTER_PAGE_SIZE = 50


class SqlCredential:
    def __init__(self, sql_id, sql_password, sql_dcf, sql_fdb):
        self.sql_id = sql_id
        self.sql_password = sql_password
        self.sql_dcf = sql_dcf
        self.sql_fdb = sql_fdb


class Sql:
    def __init__(self, sql_crendential: SqlCredential):
        self._com = win32com.client.Dispatch("SQLAcc.BizApp")

        # Use this for util.print_members
        # self._com = win32com.client.gencache.EnsureDispatch("SQLAcc.BizApp")

        self._credential = (sql_crendential.sql_id,
                            sql_crendential.sql_password,
                            sql_crendential.sql_dcf,
                            sql_crendential.sql_fdb)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self._com

    def login(self):
        if self._com.IsLogin:
            self._com.Logout()
        self._com.Login(*self._credential)

    def count_master_data(self, table_name):
        data_set = self._com.DBManager.NewDataSet(f'SELECT COUNT(*) AS Total FROM {table_name}')
        for data in util.loop_data_sets(data_set):
            return Total(data).total
        return 0

    def get_master_data(self, table_name, total, converter):
        offset = 1
        while offset <= total:
            data_set = self._com.DBManager.NewDataSet(
                f'SELECT * FROM {table_name} ROWS {offset} TO {offset + _LOAD_MASTER_PAGE_SIZE}')
            for data in util.loop_data_sets(data_set):
                yield converter(data)
            offset += _LOAD_MASTER_PAGE_SIZE + 1

    def get_master_detail_by_code(self, table_name, code, converter):
        data_set = self._com.DBManager.NewDataSet(f"SELECT * FROM {table_name} WHERE CODE='{code}'")
        for data in util.loop_data_sets(data_set):
            yield converter(data)

    def set_sales_order(self, so: dict):
        biz_object = self._com.BizObjects.Find("SL_SO")
        main_data = biz_object.DataSets.Find("MainDataSet")
        detail_data = biz_object.DataSets.Find("cdsDocDetail")

        agent = so['agent']
        customer = so['customer']
        bill_to = so['bill_to']
        ship_to = so['ship_to']

        today = datetime.now(tz=CustomTimeZone())
        doc_date = datetime.fromtimestamp(so['created_on'], tz=CustomTimeZone())

        biz_object.New()
        main_data.FindField('DocKey').value = -1
        main_data.FindField('DocNo').AsString = so['code']
        main_data.FindField('DocDate').value = doc_date
        main_data.FindField('PostDate').value = today
        main_data.FindField('Agent').AsString = agent['code']
        main_data.FindField('Description').AsString = so['description']

        # Customer
        main_data.FindField('Code').AsString = customer['code']  # Customer Account
        main_data.FindField('CompanyName').AsString = customer['company_name']
        main_data.FindField('Area').AsString = customer['area']
        main_data.FindField('Terms').AsString = customer['credit_terms']

        # Billing Info
        main_data.FindField('Attention').AsString = bill_to['attention']
        main_data.FindField('Phone1').AsString = bill_to['phone'][0]  # Optional
        main_data.FindField('Fax1').AsString = bill_to['fax'][0]  # Optional
        main_data.FindField('Address1').AsString = bill_to['address'][0]
        main_data.FindField('Address2').AsString = bill_to['address'][1]
        main_data.FindField('Address3').AsString = bill_to['address'][2]
        main_data.FindField('Address4').AsString = bill_to['address'][3]

        # Delivery Info
        main_data.FindField('BranchName').AsString = ship_to['name']
        main_data.FindField('DAttention').AsString = ship_to['attention']
        main_data.FindField('DPhone1').AsString = ship_to['phone'][0]  # Optional
        main_data.FindField('DFax1').AsString = ship_to['fax'][0]  # Optional
        main_data.FindField('DAddress1').AsString = ship_to['address'][0]
        main_data.FindField('DAddress2').AsString = ship_to['address'][1]
        main_data.FindField('DAddress3').AsString = ship_to['address'][2]
        main_data.FindField('DAddress4').AsString = ship_to['address'][3]

        for so_item in so['items']:
            detail_data.Append()
            detail_data.FindField('DtlKey').value = -1
            detail_data.FindField('DocKey').value = -1
            detail_data.FindField('Seq').value = so_item['seq']
            detail_data.FindField('ItemCode').AsString = so_item['item']['code']
            detail_data.FindField('Description').AsString = so_item['description']
            detail_data.FindField('Qty').AsFloat = so_item['quantity']
            detail_data.FindField('UOM').AsString = so_item['uom']['uom']
            detail_data.FindField('Tax').AsString = ""
            detail_data.FindField('TaxRate').AsString = ""
            detail_data.FindField('TaxInclusive').value = 0
            detail_data.FindField('UnitPrice').AsFloat = so_item['price']
            detail_data.FindField('Amount').AsFloat = str(Decimal(so_item['price']) * Decimal(so_item['quantity']))
            detail_data.FindField('TaxAmt').AsFloat = 0
            detail_data.Post()

        biz_object.Save()
        biz_object.Close()


class CustomTimeZone(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=8)

    def dst(self, dt):
        return timedelta(hours=8)
