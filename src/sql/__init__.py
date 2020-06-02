from datetime import datetime, timedelta, tzinfo
from decimal import Decimal
from typing import Optional

import pythoncom
import win32com.client

from activity_logs import ActivityLog, ActivityLogMock
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
from sql.trans.invoice_dtl import InvoiceDTL
from sql.trans.outstanding_sales_order import OutstandingSalesOrder
from sql.trans.sales_order import SalesOrder

_LOAD_MASTER_PAGE_SIZE = 50


class Sql:
    def __init__(self, log: ActivityLog = None):
        self._dispatch()
        self._log = log or ActivityLogMock()

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
            self._log.i('sql.verify_login query agent')
            rpt_obj = self.com.RptObjects.Find('Common.Agent.RO')
            rpt_obj.CalculateReport()
            self._log.i('sql.verify_login query company profiles')
            data_set = rpt_obj.DataSets.Find("cdsProfile")
            company_profile = None
            for data in util.loop_data_sets(data_set):
                self._log.i('sql.verify_login got company profile')
                company_profile = CompanyProfile(data)
            if company_profile and company_profile.company_name == company_name:
                return
        raise Exception(f'Please login to {company_name}')

    def count_master_data(self, table_name, last_modified=None):
        query = f'SELECT COUNT(*) AS Total FROM {table_name}'
        if last_modified is not None:
            query += f' WHERE LastModified > {last_modified}'
        self._log.i('sql.count_master_data query total')
        data_set = self.com.DBManager.NewDataSet(query)
        to_return = None
        for data in util.loop_data_sets(data_set):
            self._log.i('sql.count_master_data got total')
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
            self._log.i('sql.get_master_data query master data')
            data_set = self.com.DBManager.NewDataSet(query)
            for data in util.loop_data_sets(data_set):
                self._log.i('sql.get_master_data got master data')
                yield converter(data)
            offset += _LOAD_MASTER_PAGE_SIZE + 1

    def get_master_data_by_code(self, table_name, code, converter):
        query = f"SELECT * FROM {table_name} WHERE Code = '{code}'"
        self._log.i('sql.get_master_data_by_code query data')
        data_set = self.com.DBManager.NewDataSet(query)
        to_return = None
        for data in util.loop_data_sets(data_set):
            self._log.i('sql.get_master_data_by_code got data')
            to_return = converter(data)
        return to_return

    def get_master_detail_by_code(self, table_name, code, converter):
        self._log.i('sql.get_master_detail_by_code query data')
        data_set = self.com.DBManager.NewDataSet(f"SELECT * FROM {table_name} WHERE CODE='{code}'")
        for data in util.loop_data_sets(data_set):
            self._log.i('sql.get_master_detail_by_code got data')
            yield converter(data)

    def get_st_trans(self, since_trans_no=None):
        query = f'SELECT * FROM ST_TR'
        if since_trans_no is not None:
            query += f' WHERE TransNo > {since_trans_no}'
        query += ' ORDER BY TRANSNO'
        self._log.i('sql.get_st_trans query data')
        data_set = self.com.DBManager.NewDataSet(query)
        for data in util.loop_data_sets(data_set):
            self._log.i('sql.get_st_trans got result')
            yield StockTrans(data)

    def get_sl_so(self, doc_code: str) -> Optional[SalesOrder]:
        query = f"SELECT * FROM SL_SO WHERE DocNo='{doc_code}'"
        self._log.i('sql.get_sl_so query data')
        data_set = self.com.DBManager.NewDataSet(query)
        sales_order = None
        for data in util.loop_data_sets(data_set):
            self._log.i('sql.get_sl_so got data')
            sales_order = SalesOrder(data)
        return sales_order

    def get_sl_invoice_dtl(self, doc_code: str) -> Optional[SalesOrder]:
        """
        This table stores all transferred items from Sales Order to Invoice,
        count(*) equals to total item count in sales order.

        @see "Example-SL_DO to SL_IV" in "https://wiki.sql.com.my/wiki/SDK_Live#Example_External_Program"
        """
        query = f"SELECT FIRST 1 * FROM SL_IVDTL WHERE FromDocKey=(SELECT DocKey FROM SL_SO WHERE DocNo='{doc_code}')"
        data_set = self.com.DBManager.NewDataSet(query)
        invoice_dtl = None
        for data in util.loop_data_sets(data_set):
            invoice_dtl = InvoiceDTL(data)
        return invoice_dtl

    def get_outstanding_so(self, doc_code: str) -> Optional[OutstandingSalesOrder]:
        rpt_obj = self.com.RptObjects.Find('Sales.OutstandingSO.RO')
        rpt_obj.Params.Find("AllAgent").Value = True
        rpt_obj.Params.Find("AllArea").Value = True
        rpt_obj.Params.Find("AllCompany").Value = True
        rpt_obj.Params.Find("AllDocument").Value = False
        rpt_obj.Params.Find("AllItem").Value = True
        rpt_obj.Params.Find("AllItemProject").Value = True
        rpt_obj.Params.Find("AllTariff").Value = True

        rpt_obj.Params.Find('PrintOutstandingItem').Value = False
        rpt_obj.Params.Find('PrintFulfilledItem').Value = True
        rpt_obj.Params.Find("DocumentData").Value = doc_code
        rpt_obj.Params.Find("IncludeCancelled").Value = False
        rpt_obj.Params.Find("SelectDate").Value = False
        rpt_obj.Params.Find("SelectDeliveryDate").Value = False
        rpt_obj.Params.Find("SortBy").Value = "DocNo"
        rpt_obj.Params.Find("AllDocProject").Value = True
        rpt_obj.Params.Find("AllLocation").Value = True
        rpt_obj.Params.Find("AllCompanyCategory").Value = True
        rpt_obj.Params.Find("AllBatch").Value = True
        rpt_obj.Params.Find("HasCategory").Value = False
        rpt_obj.Params.Find("AllStockGroup").Value = True

        rpt_obj.CalculateReport()
        data_set = rpt_obj.DataSets.Find("cdsMain")
        record = None
        for data in util.loop_data_sets(data_set):
            record = OutstandingSalesOrder(data)
        return record

    def set_sales_order(self, so: dict):
        biz_object = self.com.BizObjects.Find("SL_SO")
        main_data = biz_object.DataSets.Find("MainDataSet")
        detail_data = biz_object.DataSets.Find("cdsDocDetail")

        try:
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
        finally:
            biz_object.Close()


class CustomTimeZone(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=8)

    def dst(self, dt):
        return timedelta(hours=8)
