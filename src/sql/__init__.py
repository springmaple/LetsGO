from datetime import datetime, timedelta, tzinfo
from decimal import Decimal

import pythoncom
import win32com.client

from sql import util
from sql.master import MasterMeta
from sql.master.agent import Agent
from sql.master.company_profile import CompanyProfile
from sql.master.customer import Customer
from sql.master.customer_branch import CustomerBranch
from sql.master.stock_item import StockItem
from sql.master.stock_item_group import StockItemGroup
from sql.master.stock_item_uom import StockItemUom
from sql.master.stock_trans import StockTrans

_LOAD_MASTER_PAGE_SIZE = 50


class Sql:
    def __init__(self):
        self._dispatch()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _dispatch(self):
        pythoncom.CoInitialize()
        self.com = win32com.client.Dispatch("SQLAcc.BizApp")
        # Use this for util.print_members
        # self.com = win32com.client.gencache.EnsureDispatch("SQLAcc.BizApp")

    def verify_login(self, company_name: str):
        if self.com.IsLogin:
            rpt_obj = self.com.RptObjects.Find('Common.Agent.RO')
            rpt_obj.CalculateReport()
            data_set = rpt_obj.DataSets.Find("cdsProfile")
            company_profile = None
            for data in util.loop_data_sets(data_set):
                company_profile = CompanyProfile(data)
            if company_profile and company_profile.company_name == company_name:
                return
        raise Exception(f'Please login to {company_name}')

    def count_master_data(self, table_name, last_modified=None):
        query = f'SELECT COUNT(*) AS Total FROM {table_name}'
        if last_modified is not None:
            query += f' WHERE LastModified > {last_modified}'
        data_set = self.com.DBManager.NewDataSet(query)
        to_return = None
        for data in util.loop_data_sets(data_set):
            to_return = MasterMeta(data).total
        return to_return or 0

    def get_master_data(self, table_name, total, converter, last_modified=None, order_by_last_modified=True):
        offset = 1
        while offset <= total:
            query = f'SELECT * FROM {table_name}'
            if last_modified is not None:
                query += f' WHERE LastModified > {last_modified}'
            if order_by_last_modified:
                query += ' ORDER BY LastModified'
            query += f' ROWS {offset} TO {offset + _LOAD_MASTER_PAGE_SIZE}'
            data_set = self.com.DBManager.NewDataSet(query)
            for data in util.loop_data_sets(data_set):
                yield converter(data)
            offset += _LOAD_MASTER_PAGE_SIZE + 1

    def get_master_data_by_code(self, table_name, code, converter):
        query = f"SELECT * FROM {table_name} WHERE Code = '{code}'"
        data_set = self.com.DBManager.NewDataSet(query)
        to_return = None
        for data in util.loop_data_sets(data_set):
            to_return = converter(data)
        return to_return

    def get_master_detail_by_code(self, table_name, code, converter):
        data_set = self.com.DBManager.NewDataSet(f"SELECT * FROM {table_name} WHERE CODE='{code}'")
        for data in util.loop_data_sets(data_set):
            yield converter(data)

    def get_st_trans(self, since_trans_no=None):
        query = f'SELECT * FROM ST_TR'
        if since_trans_no is not None:
            query += f' WHERE TransNo > {since_trans_no}'
        query += ' ORDER BY TRANSNO'
        data_set = self.com.DBManager.NewDataSet(query)
        for data in util.loop_data_sets(data_set):
            yield StockTrans(data)

    def set_sales_order(self, so: dict):
        biz_object = self.com.BizObjects.Find("SL_SO")
        main_data = biz_object.DataSets.Find("MainDataSet")
        detail_data = biz_object.DataSets.Find("cdsDocDetail")

        agent = so['agent']
        customer = so['customer']
        bill_to = so['bill_to']
        ship_to = so['ship_to']

        today = datetime.now(tz=CustomTimeZone())
        doc_date = datetime.fromtimestamp(so['created_on'], tz=CustomTimeZone())

        biz_object.New()
        main_data.FindField('DocKey').Value = -1
        main_data.FindField('DocNo').AsString = so['code']
        main_data.FindField('DocDate').Value = doc_date
        main_data.FindField('PostDate').Value = today
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
            detail_data.FindField('DtlKey').Value = -1
            detail_data.FindField('DocKey').Value = -1
            detail_data.FindField('Seq').Value = so_item['seq']
            detail_data.FindField('ItemCode').AsString = so_item['item']['code']
            detail_data.FindField('Description').AsString = so_item['description']
            detail_data.FindField('Qty').AsFloat = so_item['quantity']
            detail_data.FindField('UOM').AsString = so_item['uom']['uom']
            detail_data.FindField('Tax').AsString = ""
            detail_data.FindField('TaxRate').AsString = ""
            detail_data.FindField('TaxInclusive').Value = 0
            detail_data.FindField('UnitPrice').AsFloat = so_item['price']
            detail_data.FindField('Amount').AsFloat = str(Decimal(so_item['price']) * Decimal(so_item['quantity']))
            detail_data.FindField('TaxAmt').AsFloat = 0
            detail_data.FindField('Remark1').AsString = so_item.get('remark', '')
            detail_data.FindField('Remark2').AsString = so_item.get('remark_2', '')
            detail_data.Post()

        remark_1 = so.get('remark', '').strip()
        if remark_1:
            detail_data.Append()
            detail_data.FindField('Description').AsString = remark_1
            detail_data.Post()

        remark_2 = so.get('remark_2', '').strip()
        if remark_2:
            detail_data.Append()
            detail_data.FindField('Description').AsString = remark_2
            detail_data.Post()

        biz_object.Save()
        biz_object.Close()


class CustomTimeZone(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=8)

    def dst(self, dt):
        return timedelta(hours=8)
